"""Command line: python -m signalpost.cli run --organisations FILE --out DIR   (or: make run INPUT=FILE OUT=DIR)"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from .budget import Budget
from .bulk import BulkUnavailable, bulk_roles, bulk_subunits
from .config import Settings
from .httpcache import ApiClient, Fetched, utc_now
from .inputs import load_registry_rows, read_inputs
from .pipeline import DEFAULT_MODULES, placeholder_envelope, register_envelope
from .planner import Company, Plan, plan_batch, summarize
from .runner import build_report, read_previous, render_report, run_planned_batch
from .store import SnapshotStore
from .validate import validate_file
from .web.fetch import WebFetcher
from .web.llm import LlmClient, providers_from_env


def load_dotenv(path: str = ".env") -> None:
    """Minimal .env loader; real environment variables win. Values are never printed."""
    p = Path(path)
    if not p.exists():
        return
    for ln in p.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            k, _, v = ln.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="signalpost", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="research a batch of organisation numbers")
    r.add_argument("--organisations", "--input", required=True, help="JSON / JSONL / text list of organisation numbers")
    r.add_argument("--out", default="out", help="output directory (envelopes.jsonl, report.json, state.sqlite)")
    r.add_argument("--bulk", "--universe", dest="registry", default=None,
                   help="Brreg bulk CSV or universe JSONL(.gz): free identity fallback (default data/orgs.json)")
    r.add_argument("--previous", default=None, help="envelopes.jsonl from an earlier run, for change detection")
    r.add_argument("--store", default=None, help="SQLite snapshot store (default OUT/state.sqlite)")
    r.add_argument("--run-id", default=None)
    r.add_argument("--expected-count", type=int, default=None, help="fail (exit 2) if input count differs")
    r.add_argument("--workers", type=int, default=None)
    r.add_argument("--modules", default=None, help="fixed module list (disables the budget planner)")
    r.add_argument("--bulk-register", choices=["auto", "on", "off"], default="auto",
                   help="roles/subunits from one bulk snapshot instead of 1 request per company "
                        "(auto: from BULK_THRESHOLD companies upward)")
    r.add_argument("--no-web", action="store_true", help="register-only run")
    r.add_argument("--no-llm", action="store_true", help="deterministic web extraction only")
    r.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    t_start = time.monotonic()  # process start: the wall-clock limit covers loading and writing too
    load_dotenv()
    s = Settings.from_env()
    workers = a.workers or s.max_workers
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    run_id = a.run_id or datetime.now(UTC).strftime("run-%Y%m%dT%H%M%SZ")
    inputs = read_inputs(a.organisations)
    if a.expected_count is not None and len(inputs) != a.expected_count:
        print(f"expected {a.expected_count} organisations, got {len(inputs)}", file=sys.stderr)
        return 2
    registry = a.registry or ("data/orgs.json" if Path("data/orgs.json").exists() else None)
    rows = load_registry_rows(registry, {i.org for i in inputs if i.valid})
    prev = read_previous(a.previous) if a.previous else {}
    prefetched: dict[str, dict] = {}
    snapshot_at = utc_now()
    for org, row in rows.items():  # a bulk CSV carries the full entity record: entity module costs 0 requests
        if row.get("_entity"):
            body = row["_entity"]
            prefetched.setdefault(org, {})["entity"] = Fetched(
                f"https://data.brreg.no/enhetsregisteret/api/enheter/{org}", 200, body,
                hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
                snapshot_at, requests=0, via="bulk")
    store = SnapshotStore(a.store or out / "state.sqlite")
    # hard stop = limit - safety margin (one network timeout + final write); SIGINT/SIGTERM trigger it immediately
    budget = Budget(s.request_budget_total, s.request_budget_per_company,
                    deadline=t_start + s.wall_clock_seconds - s.cutoff_margin_seconds)
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: budget.expire())
    client = ApiClient(budget=budget)
    fetcher = None if a.no_web else WebFetcher(budget)
    providers = [] if (a.no_web or a.no_llm) else providers_from_env()
    llm = LlmClient(providers, budget) if providers else None
    fixed = tuple(m for m in a.modules.split(",") if m) if a.modules else None
    started_at = utc_now()
    valid = {i.org for i in inputs if i.valid}
    bulk_info: dict[str, object] = {"mode": a.bulk_register}
    use_bulk = a.bulk_register == "on" or (a.bulk_register == "auto" and len(valid) >= s.bulk_threshold)
    if use_bulk and valid and fixed is None:
        from concurrent.futures import ThreadPoolExecutor
        t_bulk = time.monotonic()
        if not a.quiet:
            print(f"bulk snapshots for {len(valid)} companies (roles + subunits, 2 requests total)...",
                  file=sys.stderr, flush=True)
        with ThreadPoolExecutor(2) as ex:
            futs = {"roles": ex.submit(bulk_roles, valid, budget), "subunits": ex.submit(bulk_subunits, valid, budget)}
            for module, fut in futs.items():
                try:
                    for org, fetched in fut.result().items():
                        prefetched.setdefault(org, {})[module] = fetched
                    bulk_info[module] = "ok"
                except BulkUnavailable as exc:
                    bulk_info[module] = f"unavailable ({exc}); falling back to per-company requests"
        bulk_info["seconds"] = round(time.monotonic() - t_bulk, 1)

    def plan_fn(pending):
        if fixed is not None:
            return {i.org: Plan(modules=list(fixed), web=True) for i in pending}
        cos = [Company(i.org, bool((rows.get(i.org) or {}).get("website")) and fetcher is not None,
                       (rows.get(i.org) or {}).get("industry_code", ""), frozenset(prefetched.get(i.org, {})))
               for i in pending]
        return plan_batch(cos, budget.remaining_total, s.request_budget_per_company, llm=llm is not None)

    def make(row, plan):
        plan = plan or Plan(modules=list(DEFAULT_MODULES), web=True)
        return register_envelope(row.org, client, run_id=run_id, universe_row=rows.get(row.org),
                                 modules=tuple(plan.modules), fetcher=fetcher if plan.web else None, llm=llm,
                                 store=store, previous=prev.get(row.org), accounts_attempts=plan.accounts_attempts,
                                 prefetched=prefetched.get(row.org))

    def placeholder(row, reason):
        return placeholder_envelope(row.org, rows.get(row.org), run_id, reason, previous=prev.get(row.org) or
                                    store.latest(row.org))

    def progress(done: int, total: int, elapsed: float) -> None:
        if not a.quiet and (done == total or done % max(1, total // 20) == 0):
            print(f"[{done:>{len(str(total))}}/{total}] {done / max(elapsed, 1e-9):5.1f} companies/s  "
                  f"elapsed {elapsed:6.1f}s  requests {budget.used}", file=sys.stderr, flush=True)

    first_plan = summarize(plan_fn(inputs)) if fixed is None else {"fixed_modules": list(fixed)}  # before spending
    envs, info = run_planned_batch(inputs, make, placeholder, plan_fn, run_id=run_id, workers=workers,
                                   out_path=out / "envelopes.jsonl", budget=budget, progress=progress)
    report = build_report(envs, run_id=run_id, started_at=started_at, wall_s=time.monotonic() - t_start,
                          budget_used=budget.used, expected=len(inputs), llm_usage=llm.usage if llm else None,
                          settings={"workers": workers, "web": not a.no_web,
                                    "llm_providers": [p.name for p in providers],
                                    "request_budget_total": s.request_budget_total,
                                    "request_budget_per_company": s.request_budget_per_company,
                                    "wall_clock_seconds": s.wall_clock_seconds,
                                    "cutoff_margin_seconds": s.cutoff_margin_seconds})
    report["control"] = {**{k: v for k, v in info.items() if k != "plans"}, "replans": len(info["plans"]), "bulk": bulk_info,
                         "initial_plan_estimate": first_plan, "budget_exhausted": budget.used >= budget.total}
    report["contract_validation"] = validate_file(out / "envelopes.jsonl", [i.org or i.raw for i in inputs])
    (out / "report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False, sort_keys=True) + "\n",
                                     encoding="utf-8")
    print(render_report(report))
    print(f"wrote {out / 'envelopes.jsonl'} and {out / 'report.json'}")
    return 0 if report["exactly_one_envelope_per_input"] and report["contract_validation"]["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
