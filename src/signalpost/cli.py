"""Command line: python -m signalpost.cli run --organisations FILE --out DIR   (or: make run INPUT=FILE OUT=DIR)"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from .budget import Budget
from .config import Settings
from .httpcache import ApiClient, utc_now
from .inputs import load_registry_rows, read_inputs
from .pipeline import DEFAULT_MODULES, register_envelope
from .runner import build_report, read_previous, render_report, run_batch
from .store import SnapshotStore
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
    r.add_argument("--modules", default=",".join(DEFAULT_MODULES))
    r.add_argument("--no-web", action="store_true", help="register-only run")
    r.add_argument("--no-llm", action="store_true", help="deterministic web extraction only")
    r.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

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
    store = SnapshotStore(a.store or out / "state.sqlite")
    budget = Budget(s.request_budget_total, s.request_budget_per_company)
    client = ApiClient(budget=budget)
    fetcher = None if a.no_web else WebFetcher(budget)
    providers = [] if (a.no_web or a.no_llm) else providers_from_env()
    llm = LlmClient(providers, budget) if providers else None
    modules = tuple(m for m in a.modules.split(",") if m)
    started_at, t0 = utc_now(), __import__("time").monotonic()

    def make(row):
        return register_envelope(row.org, client, run_id=run_id, universe_row=rows.get(row.org), modules=modules,
                                 fetcher=fetcher, llm=llm, store=store, previous=prev.get(row.org))

    def progress(done: int, total: int, elapsed: float) -> None:
        if not a.quiet and (done == total or done % max(1, total // 20) == 0):
            print(f"[{done:>{len(str(total))}}/{total}] {done / max(elapsed, 1e-9):5.1f} companies/s  "
                  f"elapsed {elapsed:6.1f}s  requests {budget.used}", file=sys.stderr, flush=True)

    envs = run_batch(inputs, make, run_id=run_id, workers=workers, out_path=out / "envelopes.jsonl", progress=progress)
    report = build_report(envs, run_id=run_id, started_at=started_at, wall_s=__import__("time").monotonic() - t0,
                          budget_used=budget.used, expected=len(inputs), llm_usage=llm.usage if llm else None,
                          settings={"workers": workers, "modules": list(modules), "web": not a.no_web,
                                    "llm_providers": [p.name for p in providers],
                                    "request_budget_total": s.request_budget_total,
                                    "request_budget_per_company": s.request_budget_per_company})
    (out / "report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False, sort_keys=True) + "\n",
                                     encoding="utf-8")
    print(render_report(report))
    print(f"wrote {out / 'envelopes.jsonl'} and {out / 'report.json'}")
    return 0 if report["exactly_one_envelope_per_input"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
