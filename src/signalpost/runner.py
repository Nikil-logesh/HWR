"""Batch runner: one terminal envelope per input, never dropped. Workers, progress, partial-safe writes."""
from __future__ import annotations

import json
import os
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from .httpcache import utc_now
from .inputs import InputRow
from .models import Envelope, Operations, Run


def failed_envelope(row: InputRow, run_id: str, reason: str, *, started: str | None = None, availability="failed",
                    explanation: str | None = None) -> Envelope:
    from .claims import ClaimSet
    cs = ClaimSet()
    cs.unavailable("registry_record", availability, note=reason)
    now = utc_now()
    return Envelope(organisation_number=row.org or row.raw, run=Run(run_id=run_id, started_at=started or now,
                    completed_at=now, terminal_status="failed"), claims=cs.sorted_claims(),
                    errors=[{"module": "input" if not row.valid else "runner", "error": reason}],
                    operations=Operations(), explanation=explanation or f"No profile could be produced: {reason}.")


def write_jsonl_atomic(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("".join(ln + "\n" for ln in lines), encoding="utf-8")
    os.replace(tmp, path)


def run_batch(inputs: list[InputRow], make_envelope: Callable[[InputRow], Envelope], *, run_id: str, workers: int,
              out_path: Path, progress: Callable[[int, int, float], None] | None = None,
              checkpoint_every: int = 25) -> list[Envelope]:
    """Process all inputs; results keep input order. Output file is rewritten atomically at checkpoints."""
    results: dict[int, Envelope] = {}
    lock = threading.Lock()
    t0 = time.monotonic()

    def work(i: int, row: InputRow) -> None:
        started = utc_now()
        if not row.valid:
            env = failed_envelope(row, run_id, f"invalid organisation number {row.raw!r} (needs 9 digits, mod-11)",
                                  started=started)
        else:
            try:
                env = make_envelope(row)
            except Exception as exc:  # noqa: BLE001 - a crash must still yield a terminal envelope
                env = failed_envelope(row, run_id, f"{type(exc).__name__}: {str(exc)[:200]}", started=started)
        with lock:
            results[i] = env
            done = len(results)
            if done % checkpoint_every == 0 and done < len(inputs):
                write_jsonl_atomic(out_path, [results[k].to_json_line() for k in sorted(results)])
        if progress:
            progress(done, len(inputs), time.monotonic() - t0)

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        for f in [pool.submit(work, i, r) for i, r in enumerate(inputs)]:
            f.result()
    envs = [results[i] for i in range(len(inputs))]
    write_jsonl_atomic(out_path, [e.to_json_line() for e in envs])
    return envs


def build_report(envs: list[Envelope], *, run_id: str, started_at: str, wall_s: float, budget_used: int,
                 expected: int, llm_usage: Any | None, settings: dict[str, Any]) -> dict[str, Any]:
    n = len(envs)
    avail: dict[str, int] = {}
    states: dict[str, int] = {}
    for e in envs:
        states[e.run.terminal_status] = states.get(e.run.terminal_status, 0) + 1
        for c in e.claims:
            if c.availability == "available":
                avail[c.field] = avail.get(c.field, 0) + 1
    reqs = sorted(e.operations.requests for e in envs)
    rt = sorted(e.operations.runtime_ms for e in envs)

    def pct(xs: list[int], q: float) -> int | None:
        return xs[min(len(xs) - 1, max(0, int(q * len(xs) + 0.999999) - 1))] if xs else None
    key = ["legal_name", "status", "nace", "registered_address", "employees", "roles", "financials.revenue",
           "financials.total_assets", "workplaces", "registry_website", "official_website", "website_description",
           "contact_email_1", "contact_phone_1", "social_linkedin", "social_facebook"]
    facts = sum(1 for e in envs for c in e.claims if c.availability == "available")
    return {
        "run_id": run_id, "started_at": started_at, "completed_at": utc_now(),
        "companies_input": expected, "envelopes_written": n,
        "exactly_one_envelope_per_input": n == expected and len({e.organisation_number for e in envs}) == n,
        "terminal_status_counts": states,
        "coverage_companies_with_field": {k: avail.get(k, 0) for k in key},
        "coverage_pct": {k: round(100 * avail.get(k, 0) / n, 1) if n else 0 for k in key},
        "available_facts_total": facts, "mean_facts_per_company": round(facts / n, 2) if n else 0,
        "companies_with_changes": sum(1 for e in envs if e.changes),
        "changes_total": sum(len(e.changes) for e in envs),
        "dropped_web_facts": sum(1 for e in envs for x in e.errors if x.get("kind") == "dropped_fact"),
        "carried_forward_facts": sum(1 for e in envs for c in e.claims if c.carried_forward),
        "operations": {
            "requests_total_budgeted": budget_used,
            "requests_total_envelopes": sum(e.operations.requests for e in envs),
            "requests_per_company_mean": round(sum(reqs) / n, 2) if n else 0,
            "requests_per_company_p95": pct(reqs, 0.95), "requests_per_company_max": reqs[-1] if reqs else 0,
            "company_runtime_ms_p50": pct(rt, 0.5), "company_runtime_ms_p95": pct(rt, 0.95),
            "wall_clock_seconds": round(wall_s, 2),
            "third_party_cost_usd": round(llm_usage.cost_usd, 6) if llm_usage else 0.0,
            "llm": ({"requests": llm_usage.requests, "prompt_tokens": llm_usage.prompt_tokens,
                     "completion_tokens": llm_usage.completion_tokens, "failures": llm_usage.failures,
                     "by_provider": llm_usage.by_provider} if llm_usage else None),
        },
        "settings": settings,
    }


def render_report(r: dict[str, Any]) -> str:
    o = r["operations"]
    lines = [
        (f"Run {r['run_id']}: {r['envelopes_written']}/{r['companies_input']} envelopes "
         f"(one per input: {r['exactly_one_envelope_per_input']}), status {r['terminal_status_counts']}"),
        (f"Time {o['wall_clock_seconds']}s | requests {o['requests_total_budgeted']} "
         f"(mean {o['requests_per_company_mean']}/company, p95 {o['requests_per_company_p95']}) | "
         f"cost ${o['third_party_cost_usd']}"),
        "Coverage (companies with field):"]
    lines += [f"  {k:<26}{r['coverage_companies_with_field'][k]:>6}  {r['coverage_pct'][k]:>5}%"
              for k in r["coverage_pct"]]
    lines.append(f"Changes: {r['changes_total']} in {r['companies_with_changes']} companies | dropped web facts: "
                 f"{r['dropped_web_facts']} | carried forward: {r['carried_forward_facts']}")
    return "\n".join(lines)


def read_previous(path: str | Path) -> dict[str, Envelope]:
    prev: dict[str, Envelope] = {}
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        if ln.strip():
            e = Envelope.model_validate(json.loads(ln))
            prev[e.organisation_number] = e
    return prev
