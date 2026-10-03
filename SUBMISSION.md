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
  Google AI Studio. **No model has been benchmarked** (no keys were available): `BENCHMARK.md` is marked NOT RUN and
  recommends nothing. Candidate IDs confirmed in the NVIDIA catalogue: `deepseek-ai/deepseek-v4.1-flash`,
  `google/gemma-4-31b-it`, `openai/gpt-oss-20b`, `nvidia/nemotron-3.5-lightning-30b-a3b`. If Builderr supplies a model key
  (RULES.md allows asking), set `LLM_PRIMARY_*`; otherwise the agent runs without an LLM.
* **Dependency licences** (MIT / BSD / Apache-2.0 only) and full source-rights, secrets and URL-safety declarations:
  `LIMITATIONS.md`. No restricted platform (LinkedIn, Meta, Glassdoor, Indeed, Google/Bing results) is used.

## Expected cost
| | requests | third-party cost |
|---|---|---|
| **Measured, 100 companies** (smoke test, no LLM) | 320 (3.2 per company, max 5) | $0 |
| **Measured, 1,500 companies** (bulk roles/workplaces/entity, no LLM) | 1,834 (1.22 per company), 288 s | $0 |
| LLM add-on (not measured) | at most 1 call per company that lists a website (~11%): ~25k tokens per 100 companies | NVIDIA free tier: $0 (declared, unverified); Gemini Flash-Lite at the declared 0.10/0.40 USD per M tokens: ≈ $0.003 per 100 companies, ≈ $0.03 per 1,000 |

Website requests (≤4 per website, throttled) were **not** exercised live; the planner budgets 4–5 per website-listing company
(about 11% of companies). Official limits are unpublished: our defaults are 45 min / 2,000 requests / $10, configurable.

## Checklist against RULES.md "Official-run checks" and the kit's submission contract
| Requirement | Status | Evidence |
|---|---|---|
| No fabricated financial values | **Met by construction** | values only from Regnskapsregisteret numbers (`accounts.py`); test compares every published value with the raw filing for 12 real companies; validator rejects any financial claim not from the official API; LLM never sees financials |
| No material wrong-company publication | **Designed + tested on synthetic pages; NOT verified live** | identity gate (`IDENTITY_RESOLUTION.md`), verifier, fail-closed; `make audit` found 0 hard flags in 1,500 profiles, but those contain no web facts (sandbox could not reach websites) |
| 100-company smoke-test result in the public artifact | Met | `reports/smoke-test-100/` |
| Exactly one terminal envelope per input | Met | 100/100 and 1,500/1,500; invalid ids and crashes still get a `failed` envelope; cutoff writes placeholders (`tests/test_budget_control.py`) |
| Claim-level source, retrieval time, reporting period | Met | `signalpost.validate` runs in every run (`report.json › contract_validation`) |
| Honest availability states, never zero | Met | six states; missing omitted; real 0 kept; hiring / dated activity are **not collected** and the explanation says so |
| Idempotent refresh, prior snapshots preserved | Met on replays and live reruns | `REFRESH.md`; refresh run: 0 changes, identical results; no duplicate snapshot rows |
| Reproducible setup, pinned deps, one evaluator command | Met | `uv.lock`; fresh-clone check recorded below |
| Declared source rights, server-side secrets, safe URL handling | Met | `LIMITATIONS.md` (key-leak test, SSRF guard, robots.txt) |
| Previous-snapshot input and material-change output | Met | `--previous`, `OUT/state.sqlite`, `changes[]` |
| Machine-readable run report with runtime, requests, cost | Met | `report.json` |

## Open items (cannot be closed inside this sandbox)
1. **Envelope shape:** we follow `kit/OUTPUT_CONTRACT.md`; the kit's reference runner emits a different legacy shape.
   Ask Builderr which one the evaluator reads (and whether a validator exists).
2. **Web layer on real sites:** run a batch where websites are reachable and audit it (`make batch` + `make audit`).
3. **LLM choice:** supply keys and run `make bench-models`; until then no model is recommended.
4. **Official time / request / cost budgets** are unpublished; confirm them, or the defaults above apply.
5. **Missing external families:** hiring and dated public activity are not collected (recall points on those are zero).
6. **Revisions:** up to four more commit hashes may be submitted before 18 Oct 2026 (five versions total); each revision
   is frozen before its next official run.
