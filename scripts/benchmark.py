#!/usr/bin/env python3
"""Run the 100-company daily-test set and compare time / requests / cost with the limits.

    uv run python scripts/benchmark.py [--input samples/daily.jsonl] [--out out/bench] [--rerun] [--no-llm]

Limits (internal safety limits; official limits are not published): 45 min, 2000 outbound requests, $10 declared
external cost; targets: < 15 requests per company, $0 on free models. Exit code 1 when any limit is exceeded.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "kit" / "src")]

from signalpost.cli import main as cli_main

WEB_WORST_CASE = 5  # robots.txt + homepage + 2 secondary pages + 1 LLM call


def row(name, measured, limit, ok):
    print(f"  {name:<34}{measured:>14}{limit:>14}   {'PASS' if ok else 'FAIL'}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(ROOT / "samples" / "daily.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "out" / "bench"))
    ap.add_argument("--rerun", action="store_true", help="second run on the same state: measures refresh")
    ap.add_argument("--no-llm", action="store_true")
    ap.add_argument("--limit-seconds", type=float, default=2700)
    ap.add_argument("--limit-requests", type=int, default=2000)
    ap.add_argument("--limit-cost", type=float, default=10.0)
    ap.add_argument("--limit-per-company", type=float, default=15)
    a = ap.parse_args()
    n = sum(1 for ln in Path(a.input).read_text().splitlines() if ln.strip())
    passes = []
    for label in (["first run", "refresh run"] if a.rerun else ["first run"]):
        out = Path(a.out)
        extra = ["--no-llm"] if a.no_llm else []
        print(f"\n=== benchmark: {label} ({n} companies) ===")
        rc = cli_main(["run", "--organisations", a.input, "--out", str(out), "--expected-count", str(n), "--quiet",
                       "--run-id", f"bench-{label.split()[0]}", *extra])
        rep = json.loads((out / "report.json").read_text())
        o, cov = rep["operations"], rep["coverage_companies_with_field"]
        sites = cov.get("registry_website", 0)
        projected = o["requests_total_budgeted"] + sites * WEB_WORST_CASE
        print(f"\n  {'metric':<34}{'measured':>14}{'limit':>14}")
        ok = [
            row("wall clock (s)", o["wall_clock_seconds"], a.limit_seconds, o["wall_clock_seconds"] <= a.limit_seconds),
            row("outbound requests (measured)", o["requests_total_budgeted"], a.limit_requests,
                o["requests_total_budgeted"] <= a.limit_requests),
            row("requests incl. worst-case web*", projected, a.limit_requests, projected <= a.limit_requests),
            row("requests/company mean", o["requests_per_company_mean"], a.limit_per_company,
                o["requests_per_company_mean"] < a.limit_per_company),
            row("requests/company max", o["requests_per_company_max"], a.limit_per_company,
                o["requests_per_company_max"] <= a.limit_per_company),
            row("third-party cost (USD)", o["third_party_cost_usd"], a.limit_cost,
                o["third_party_cost_usd"] <= a.limit_cost),
            row("one envelope per input", rep["exactly_one_envelope_per_input"], True,
                rep["exactly_one_envelope_per_input"]),
            row("contract validation", rep["contract_validation"]["passed"], True, rep["contract_validation"]["passed"]),
            row("cutoff triggered", rep["control"]["cutoff_triggered"], False, not rep["control"]["cutoff_triggered"]),
        ]
        print(f"  * worst case assumes {WEB_WORST_CASE} requests for each of the {sites} companies listing a website "
              f"(websites are unreachable from some sandboxes, so measured web traffic may be understated)")
        print(f"  runtime/company p50 {o['company_runtime_ms_p50']} ms, p95 {o['company_runtime_ms_p95']} ms | "
              f"changes {rep['changes_total']} | status {rep['terminal_status_counts']} | rc={rc}")
        passes += ok + [rc == 0]
    print("\nBENCHMARK", "PASSED" if all(passes) else "FAILED")
    return 0 if all(passes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
