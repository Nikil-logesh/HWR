# 100-company smoke test

Input: `samples/daily.jsonl` (100 companies, seeded random draw from the 411,160-company universe, seed 20261003).
Code: the tree of commit `49b58f9` plus the one-line careers-link fix committed right after it (the commit that adds these
result files; `git log` shows it). Date: 2026-10-04, from a sandbox that **could reach company websites** (so, unlike the
2026-10-03 run it replaces, the 10 companies that list a website were really fetched). No LLM (`--no-llm`).
Command (identical for both runs; the second reuses `out/smoke3/state.sqlite`, i.e. it is a refresh run):

    uv run python run_agent.py run --organisations samples/daily.jsonl --bulk brreg-enheter.csv.gz \
        --out out/smoke3 --expected-count 100 --no-llm --run-id smoke-first|smoke-refresh \
        --output <dir>/envelopes.jsonl --report <dir>/report.json --html <dir>/report.html

| | first run | refresh run |
|---|---|---|
| envelopes (one per input, contract-validated) | 100 / 100 | 100 / 100 |
| terminal status | 100 completed | 100 completed |
| wall clock | 52.0 s | 44.5 s |
| outbound requests | 343 (mean 3.43, p95 7, max 9 per company) | 337 (p95 6, max 9) |
| third-party cost | $0 | $0 |
| changes detected | 0 | 0 (all claims identical to the first run) |
| wrong-company audit (`scripts/audit_sample.py`) | 0 hard / 0 soft flags | |

Coverage (companies with the field): legal name, status, NACE, registered address, roles, total assets 100%;
workplaces 78%; revenue 74%; employee count 18%; registry-listed website 10%.

**Website layer in this run:** 10 companies list a website: 6 verified (3 with a description, 4 with an email, 3 with a
phone, 1 with dated feed activity, 0 careers pages, 0 job listings), 1 `ambiguous` (the page does not name the company),
3 not reachable or refused (robots.txt / HTTP 403 / proxy error). The second run issues a few requests fewer because some of
those unreachable sites fail faster; claims are identical. The web facts of the 6 verified sites were read by hand against
their snippets; one false positive was found in this run (a coaching-course article taken for a careers page because its URL
contained `bli-med`) and fixed with a regression test before these results were recorded.

**What this run does not show.** Ten websites are too few to say anything about web precision or coverage; see
`REAL_WEB_FINDINGS.md` (150 real sites) and `LIMITATIONS.md`. No LLM was used. Roles and workplaces were fetched per company
because 100 < `BULK_THRESHOLD` (300); the entity record came free from the bulk CSV.
Files: `*/envelopes.jsonl` (the 100 envelopes), `*/report.json` (machine-readable run report), `first-run/report.html`
(human-readable viewer), `*/console.txt` (progress and final summary).
