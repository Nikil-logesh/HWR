# Signalpost agent

Give it Norwegian organisation numbers; it returns one evidence-bound company profile per number: official register
facts, filed accounts, leadership, workplaces and — only when a page proves it is the same legal entity — website
facts. Every fact carries `{value, source_url, retrieved_at, evidence_snippet, content hash, confidence}`; missing
information is an explicit state, never zero. Re-running it keeps profiles current and lists what changed.

Built for the Builderr *Signalpost* challenge. The repository follows `RULES.md` > `kit/` (the Builderr starter kit,
unmodified, used as a library) > the original task brief.

## Quick start

Requires `uv` (https://docs.astral.sh/uv/) and network access. Python 3.12 is fetched by `uv` automatically.

```bash
git clone <REPO_URL> signalpost && cd signalpost
uv sync --frozen --python 3.12            # the only install step (pinned by uv.lock)

# one command: a batch of organisation numbers in, one envelope per number out
uv run python run_agent.py run --organisations companies.jsonl --out out/
# equivalent:  make run INPUT=companies.jsonl OUT=out/
```

`companies.jsonl` is a JSON list, JSONL (`{"organisation_number": "923609016"}`) or one number per line.

Recommended for the official run — add the Brønnøysund bulk snapshot (it makes the entity record free):

```bash
curl -L https://data.brreg.no/enhetsregisteret/api/enheter/lastned/csv -o brreg-enheter.csv.gz   # ~155 MB
uv run python run_agent.py run --organisations companies.jsonl --bulk brreg-enheter.csv.gz --out out/
```

The file is detected by content, so a gzip download saved as `.csv` also works. Without `--bulk` the agent still works
(it reads each entity record from the API, within the request budget). Git LFS is **not** required.

Outputs in `out/`: `envelopes.jsonl` (one JSON object per input, same order), `report.json` (machine-readable run
report: coverage, requests, cost, time, validation), `report.html` (self-contained, mobile-friendly viewer with search,
sources and evidence snippets), `state.sqlite` (previous profiles, used for refresh).

Kit-compatible flags are accepted: `--output`, `--profiles-output`, `--report`, `--run-id`, `--expected-count`,
`--resume`, `--checkpoint-every`.

### Refresh (keep profiles current)
Run again with the same `--out` (state is in `out/state.sqlite`) or pass `--previous old/envelopes.jsonl`. Each envelope's
`changes[]` lists `field, old_value, new_value, change_type, material, detected_at` and both sides' sources; unchanged
facts keep `first_observed_at` and get a new `last_checked_at`; a failing source never erases the last supported value.

### Optional LLM
Copy `.env.example` to `.env` and set `LLM_PRIMARY_*` (NVIDIA build, OpenAI-compatible) and/or `LLM_FALLBACK_*`
(Gemini Flash-Lite). Without keys the agent runs with deterministic extraction only (`--no-llm` forces that). The model
only proposes verbatim description/service text from already-fetched, identity-verified pages; code verifies every snippet.

## Output (envelope)
One object per input, matching `kit/OUTPUT_CONTRACT.md`: `organisation_number`, `run`, `claims[]` (`field`, `value`,
`availability` ∈ available / not_available / blocked / not_applicable / ambiguous / failed, `confidence`,
`evidence_ids`, `reporting_period`, `first_observed_at`, `last_checked_at`), `evidence[]` (`source_url`,
`source_class`, `retrieved_at`, `content_sha256`, `claim_span`, `extraction_method`), `changes[]`, `errors[]`,
`operations` (requests, runtime, third-party cost), `explanation` (2–4 plain-language sentences) and `schema_version`.
Details: `DATA_SCHEMA.md`.

## How it works
1. **Register layer (no LLM).** The organisation number is the identity anchor. Entity facts come from the Brønnøysund
   bulk CSV or API; roles and registered workplaces from one bulk snapshot each (or per-company calls for small batches);
   financial values **only** from the Regnskapsregisteret JSON numbers, with reporting period. Missing is omitted, a real
   0 is kept.
2. **Website layer, fail-closed.** Only the website listed in the register is visited (robots.txt honoured, ≤7 requests,
   throttled). A page is accepted only if code finds the organisation number, or the legal name plus street address /
   postcode+city / registered phone. A different organisation number on the page vetoes it. Below 0.90 identity score
   nothing from the web is published (`ambiguous`). ~89% of companies list no website: for those the agent tries domain names built from the legal name (candidates only,
   accepted only on the organisation number or full name + exact street; `--no-discovery` turns it off).
   Contacts are attributed to the company's own address/name block on the page, never to a sister unit or the group.
   On a verified site the agent also looks for **hiring** (careers page: job postings, "no open positions", external
   portal link) and **dated activity** (RSS feed / news page), conservatively and with per-item evidence; a site that
   names other organisation numbers is treated as a possible group site and yields nothing.
3. **Literal-snippet verifier.** A web fact is kept only if its evidence snippet occurs in the fetched page and contains
   the value. LLM output that fails this is dropped.
4. **Refresh.** Snapshots are stored (identical reruns add no duplicate rows); diffs produce typed, material-flagged changes.
5. **Budget control.** A planner spends the request budget on the highest-value modules first and re-plans every chunk; a
   hard wall-clock deadline (or SIGTERM) switches to zero-network placeholder envelopes so the output file always holds
   one valid line per input.
6. **Explanations.** Each profile gets a deterministic note: what was found and from where, confidence, conflicts
   (e.g. website phone vs register), changes, and what was not collected.

## Verify it
```bash
make test                                   # 273 tests, no network needed
make bench                                  # 100-company daily-test benchmark vs time/request/cost limits (live Brreg)
make batch BULK=brreg-enheter.csv.gz && make audit   # 1,500 seeded profiles + wrong-company audit + 50-profile review sheet
uv run python scripts/model_benchmark.py --help      # LLM benchmark (needs keys)
```
`reports/smoke-test-100/` holds the 100-company smoke-test result (first run and refresh run).

## Configuration (`.env`, all optional)
`REQUEST_BUDGET_TOTAL` (2000), `REQUEST_BUDGET_PER_COMPANY` (15), `WALL_CLOCK_SECONDS` (2700),
`CUTOFF_MARGIN_SECONDS` (90), `MAX_WORKERS` (8), `BULK_THRESHOLD` (300), `LLM_PRIMARY_*`, `LLM_FALLBACK_*`.
The limits are our own safety defaults; the official budgets are not published.

## Limitations (important)
The web layer has run on one sample of **150 real websites** (48 verified, 68 refused as ambiguous, 28 unreachable,
4 blocked by robots.txt; hand review found and fixed precision defects, `REAL_WEB_FINDINGS.md`), the LLM benchmark used a
proxy corpus (`BENCHMARK.md`), and the hiring extractor has not yet recognised a real job posting (0 in that sample).
See **LIMITATIONS.md** for the full list, source rights, secrets and URL-safety declarations.

## Repository map
`run_agent.py` entry point · `src/signalpost/` (`pipeline`, `register`, `accounts`, `bulk`, `planner`, `refresh`,
`store`, `explain`, `audit`, `htmlreport`, `web/` identity·fetch·verify·llm·signals) · `scripts/` (benchmarks, audit, fixture
recorder) · `tests/` (273 tests; real recorded Brreg fixtures + synthetic edge cases) · `samples/` (seeded samples) ·
`kit/` (Builderr starter kit, untouched).
Docs: `ARCHITECTURE.md`, `DATA_SCHEMA.md`, `IDENTITY_RESOLUTION.md`, `REFRESH.md`, `BUDGET.md`, `AUDIT.md`,
`BENCHMARK.md`, `REAL_WEB_FINDINGS.md`, `LIMITATIONS.md`, `SUBMISSION.md`.
