# Submission pack — Signalpost agent

Email to `submit@builderr.ai` (RULES.md "Submit"). Fill the bracketed items; everything else is ready.

| Item | Value |
|---|---|
| Agent name | Signalpost agent |
| Contact for results | [your name / email] |
| Repository URL | `<REPO_URL>` (the repository this file is in; GitHub: https://github.com/Nikil-logesh/HWR, branch `claude/hwr-repo-clone-8mv0g6`) |
| **Exact commit hash** | run `git rev-parse HEAD` **after the last commit** and paste the 40-character result. Never paste an older hash: every commit changes it. Check with `git status` (must be clean) and `git log origin/<branch> -1` (must be pushed). |
| 100-company smoke-test result | `reports/smoke-test-100/` (first run + refresh run, `README.md`, `report.json`, envelopes, HTML viewer) |
| One run command | see below |
| Models / APIs / licences | see below |
| Expected cost per official batch | see below |

## Run command
Install (only step): `uv sync --frozen --python 3.12` (dependencies pinned in `uv.lock`).
Run:

    uv run python run_agent.py run --organisations <batch.jsonl> --bulk <brreg-enheter.csv.gz> --out <outdir>

`--organisations` accepts JSON / JSONL / text; `--bulk` is the Brønnøysund bulk snapshot (optional but recommended; the
kit's flags `--output --profiles-output --report --run-id --expected-count --resume --checkpoint-every` are also
accepted). Output: `<outdir>/envelopes.jsonl` (exactly one envelope per input, same order), `report.json`, `report.html`.
Equivalent: `make run INPUT=<batch.jsonl> OUT=<outdir> BULK=<csv>`.
Environment variables (all optional): `REQUEST_BUDGET_TOTAL`, `REQUEST_BUDGET_PER_COMPANY`, `WALL_CLOCK_SECONDS`,
`CUTOFF_MARGIN_SECONDS`, `MAX_WORKERS`, `BULK_THRESHOLD`, `LLM_PRIMARY_*`, `LLM_FALLBACK_*`. Secrets only via environment.

## Models, APIs, licences, source rights
* **Official data (no key, no cost):** Brønnøysundregistrene Enhetsregisteret API + bulk files and Regnskapsregisteret
  API (data.brreg.no), NLOD 2.0. Company websites listed in the register (robots.txt honoured).
* **LLM (optional, off by default):** primary NVIDIA build endpoint (OpenAI-compatible), fallback Gemini Flash-Lite via
  Google AI Studio. Three NVIDIA models were benchmarked on a **proxy corpus** (real Norwegian company text, not real
  websites): `google/gemma-4-31b-it` (only eligible model, borderline on timeouts), `openai/gpt-oss-20b` (most reliable but
  followed 1 of 3 prompt injections), `nvidia/nemotron-3.5-lightning-30b-a3b` (27% failures). `deepseek-ai/deepseek-v4.1-flash`
  timed out on every call; Gemini Flash-Lite was not measured. Details and caveats: `BENCHMARK.md`. The agent also runs
  without any LLM (default when no key is set).
* **Dependency licences** (MIT / BSD / Apache-2.0 only) and full source-rights, secrets and URL-safety declarations:
  `LIMITATIONS.md`. No restricted platform (LinkedIn, Meta, Glassdoor, Indeed, Google/Bing results) is used.

## Expected cost
| | requests | third-party cost |
|---|---|---|
| **Measured, 100 companies** (smoke test, no LLM) | 320 (3.2 per company, max 5) | $0 |
| **Measured, 1,500 companies** (bulk roles/workplaces/entity, no LLM) | 1,834 (1.22 per company), 288 s | $0 |
| LLM add-on (not measured) | at most 1 call per company that lists a website (~11%): ~25k tokens per 100 companies | NVIDIA free tier: $0 (declared, unverified); Gemini Flash-Lite at the declared 0.10/0.40 USD per M tokens: ≈ $0.003 per 100 companies, ≈ $0.03 per 1,000 |

Website requests (≤7 per website incl. careers/news/feed, throttled) were **not** exercised live; the planner budgets 7–8 per website-listing company
(about 11% of companies). Official limits are unpublished: our defaults are 45 min / 2,000 requests / $10, configurable.

## Checklist against RULES.md "Official-run checks" and the kit's submission contract
| Requirement | Status | Evidence |
|---|---|---|
| No fabricated financial values | **Met by construction** | values only from Regnskapsregisteret numbers (`accounts.py`); test compares every published value with the raw filing for 12 real companies; validator rejects any financial claim not from the official API; LLM never sees financials |
| No material wrong-company publication | **Designed; run on 150 real sites; hand review found and fixed defects; residual risk on chain/group sites** | identity gate (`IDENTITY_RESOLUTION.md`), verifier, fail-closed; `make audit`: 0 hard flags in 1,500 register-only profiles and 0 in 150 real-website profiles, but the automated audit missed every defect the hand review found (`REAL_WEB_FINDINGS.md`) |
| 100-company smoke-test result in the public artifact | Met | `reports/smoke-test-100/` |
| Exactly one terminal envelope per input | Met | 100/100 and 1,500/1,500; invalid ids and crashes still get a `failed` envelope; cutoff writes placeholders (`tests/test_budget_control.py`) |
| Claim-level source, retrieval time, reporting period | Met | `signalpost.validate` runs in every run (`report.json › contract_validation`) |
| Honest availability states, never zero | Met | six states; missing omitted; real 0 kept; hiring / dated activity come only from a verified company site (real sample: 8 careers pages, 0 recognised listings, 8 dated feeds); profiles without one say they were not collected |
| Idempotent refresh, prior snapshots preserved | Met on replays and live reruns | `REFRESH.md`; refresh run: 0 changes, identical results; no duplicate snapshot rows |
| Reproducible setup, pinned deps, one evaluator command | Met | `uv.lock`; fresh-clone check recorded below |
| Declared source rights, server-side secrets, safe URL handling | Met | `LIMITATIONS.md` (key-leak test, SSRF guard, robots.txt) |
| Previous-snapshot input and material-change output | Met | `--previous`, `OUT/state.sqlite`, `changes[]` |
| Machine-readable run report with runtime, requests, cost | Met | `report.json` |

## Open items (cannot be closed inside this sandbox)
1. **Envelope shape:** we follow `kit/OUTPUT_CONTRACT.md`; the kit's reference runner emits a different legacy shape.
   Ask Builderr which one the evaluator reads (and whether a validator exists).
2. **Web layer on more real sites:** one 150-site sample is done (`REAL_WEB_FINDINGS.md`); a second, differently drawn sample
   (including companies whose site is a chain/group page) would show whether other defect classes exist.
3. **LLM choice:** benchmarked on a proxy corpus only; re-run with `--source web` (websites are reachable now), and
   measure Gemini Flash-Lite (needs a Google key) and re-test DeepSeek.
4. **Official time / request / cost budgets** are unpublished; confirm them, or the defaults above apply.
5. **Hiring and dated activity** are extracted only from the company's own verified website (careers page, RSS feed / news
   page) by conservative heuristics; on the real sample they found no job listing and 8 dated feeds. ~89% of companies list no
   website, so they get neither.
6. **Revisions:** up to four more commit hashes may be submitted before 18 Oct 2026 (five versions total); each revision
   is frozen before its next official run.

## Fresh-clone check (recorded 2026-10-03, verified at commit `11efc71`)
Clean directory, `GIT_LFS_SKIP_SMUDGE=1 git clone --branch claude/hwr-repo-clone-8mv0g6 <repo>` (so `data/orgs.json` was only
an LFS pointer), then only the documented steps:
* `uv sync --frozen --python 3.12` — succeeded from `uv.lock` into the clone's own `.venv`.
* `uv run pytest -q` — 213 passed, 1 skipped (the skipped test needs the LFS file).
* `uv run python run_agent.py run --organisations ten.jsonl --out out1 --expected-count 10` (no `--bulk`) — 10/10 envelopes.
* the same with `--bulk` pointing at the Brønnøysund download saved under the kit's `.csv` name (it is gzip) — 10/10
  envelopes, contract validation passed, entity facts taken from the bulk file, 32 requests (3.2 per company).
* `make run INPUT=… OUT=… BULK=…` — 10/10 envelopes. The clone stayed clean (`git status` empty).
Documentation-only commits after `11efc71` do not change this result; re-run the check if code changes.
