# 100-company smoke test

Input: `samples/daily.jsonl` (100 companies, seeded random draw from the 411,160-company universe, seed 20261003).
Code: commit `4553bf5` (website discovery, hiring/activity, contact attribution included; later commits change
documentation and result files only). Date: 2026-10-04, from a sandbox that could reach company websites. No LLM (`--no-llm`).
Command (identical for both runs; the second reuses `out/smoke4/state.sqlite`, i.e. it is a refresh run):

    uv run python run_agent.py run --organisations samples/daily.jsonl --bulk brreg-enheter.csv.gz \
        --out out/smoke4 --expected-count 100 --no-llm --run-id smoke-first|smoke-refresh \
        --output <dir>/envelopes.jsonl --report <dir>/report.json --html <dir>/report.html

| | first run | refresh run |
|---|---|---|
| envelopes (one per input, contract-validated) | 100 / 100 | 100 / 100 |
| terminal status | 100 completed | 100 completed |
| wall clock | 98.7 s | 85.0 s |
| outbound requests | 658 (mean 6.58, p95 10, max 13 per company) | 637 (p95 10, max 11) |
| third-party cost | $0 | $0 |
| changes detected | 0 | 0 (all claims identical to the first run) |
| wrong-company audit (`scripts/audit_sample.py`) | 0 hard / 0 soft flags | |

Coverage (companies with the field): legal name, status, NACE, registered address, roles, total assets 100%;
workplaces 78%; revenue 74%; employee count 18%; registry-listed website 10%; **verified website 14%** (6 registered + 8
found by website discovery); description 8%, email 10%, phone 11%.

**Website layer in this run:** 14 verified sites. The 8 discovered ones come from companies with no registered website: domain
names built from the legal name were tried and each site was accepted only because it shows the organisation number or the full legal
name with the exact street (identity snippets read by hand: all matched). The request count is higher than the earlier
register-only runs (3.4 per company) because ~3 requests per company go to guessed domains, mostly ones that do not exist.
The refresh run issues fewer requests because a site found earlier is re-checked directly instead of re-guessed.

**What this run does not show.** 100 companies are too few to say anything about web precision or coverage; see
`REAL_WEB_FINDINGS.md` (150 real sites + 200 discovery companies) and `LIMITATIONS.md`. No LLM was used. Roles and workplaces were
fetched per company because 100 < `BULK_THRESHOLD` (300); the entity record came free from the bulk CSV.
Files: `*/envelopes.jsonl` (the 100 envelopes), `*/report.json` (machine-readable run report), `first-run/report.html`
(human-readable viewer), `*/console.txt` (progress and final summary).
