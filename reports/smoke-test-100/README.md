# 100-company smoke test

Input: `samples/daily.jsonl` (100 companies, seeded random draw from the 411,160-company universe, seed 20261003).
Code: commit `6a04543` (later commits change documentation only). Date: 2026-10-03.
Command (identical for both runs; the second reuses `out/smoke/state.sqlite`, i.e. it is a refresh run):

    uv run python run_agent.py run --organisations samples/daily.jsonl --bulk brreg-enheter.csv.gz \
        --out out/smoke --expected-count 100 --no-llm --run-id smoke-first|smoke-refresh \
        --output <dir>/envelopes.jsonl --report <dir>/report.json --html <dir>/report.html

| | first run | refresh run |
|---|---|---|
| envelopes (one per input, contract-validated) | 100 / 100 | 100 / 100 |
| terminal status | 100 completed | 100 completed |
| wall clock | 29.0 s | 28.4 s |
| outbound requests | 320 (mean 3.2, p95 5, max 5 per company) | 320 |
| third-party cost | $0 | $0 |
| changes detected | 0 | 0 (idempotent) |
| wrong-company audit (`scripts/audit_sample.py`) | 0 hard / 0 soft flags | |

Coverage (companies with the field): legal name, status, NACE, registered address, roles, total assets 100%;
workplaces 78%; revenue 74%; employee count 18%; registry-listed website 10%.

**What this run does not show.** The sandbox that produced it could not reach company websites and had no LLM keys, so the
10 companies that list a website returned `failed` for the website (no web facts) and no LLM was used (`--no-llm`).
Web coverage and web precision are therefore unmeasured; see `LIMITATIONS.md`. Roles and workplaces were fetched
per company because 100 < `BULK_THRESHOLD` (300); the entity record came free from the bulk CSV.
Files: `*/envelopes.jsonl` (the 100 envelopes), `*/report.json` (machine-readable run report), `first-run/report.html`
(human-readable viewer), `*/console.txt` (progress and final summary).
