# Limitations, source rights, secrets and URL safety

## Known limitations (read before trusting a number)
1. **The web layer has run on one real sample of 150 websites, not more.** (`REAL_WEB_FINDINGS.md`, `reports/real-web-150/`.)
   48 sites were verified; hand review of their facts found precision defects that the automated audit (0 flags) could
   not see; they were fixed and have regression tests. That sample was chosen from companies that list a website, so its
   coverage figures are not representative of an official batch, there is no error bar, and a different sample may show
   defects not seen here. Some chain/association/group sites still pass the gate (the company's own name and address
   appear on them); the contacts are restricted to the company's own block but the residual risk is not zero. Some fetch
   failures (`ProxyError`, plain `http://` refused with 403) may be specific to the build sandbox.
2. **LLM benchmarked only on a proxy corpus.** `BENCHMARK.md` has real results for three NVIDIA-hosted models on real
   Norwegian company text in synthetic page boilerplate, not on real websites; Gemini Flash-Lite and DeepSeek were not
   measured (no key / timeouts). Only one model met the thresholds (gemma-4-31b-it, borderline on failures). The pipeline
   works without any LLM (deterministic extraction).
3. **Hiring and dated activity are collected only from the company's own verified website.** On the 150-site sample:
   8 careers pages, **0 recognised job listings**, 1 "no open positions" statement, 8 sites with dated feed activity;
   the job-listing heuristics have therefore **never recognised a real posting** (see `IDENTITY_RESOLUTION.md`). Recall will be low by design: precision comes first,
   so a job listing needs deadline/employment context, news items need a real visible date, external recruitment
   portals are only recorded as a link (never fetched), and a site that also names other organisation numbers (possible
   group site) yields `ambiguous`, not facts. JavaScript-rendered career pages are invisible to the static fetch. Companies
   without a listed website (~89%) get neither. No search-engine, job-board, LinkedIn, Meta or review-site collection is
   performed (restricted platforms; search results are not evidence).
4. **Group structure and annual-report PDF parsing are not implemented.** Financial history comes from the multi-year
   accounts response; filing-year lists are opt-in (rate-limited endpoint).
5. **Envelope shape.** The agent follows `kit/OUTPUT_CONTRACT.md`. The kit's reference runner emits a different legacy
   envelope (`state`, `modules`, `profile`) and the kit ships no validator for the contract; `signalpost.validate` is our
   own. Which shape the official evaluator reads is unconfirmed and should be asked of Builderr.
6. **Limits are assumed.** Official time/request/cost budgets are not published. Defaults (45 min, 2,000 requests,
   $10) are our own safety limits, configurable in `.env`.
7. **Bulk downloads cost time.** The roles and workplaces snapshots are ~130 MB + ~89 MB (about 2 minutes here); they are
   used from 300 companies upward (`BULK_THRESHOLD`). If either fails the agent falls back to per-company requests.
8. **Brreg quirks seen live:** the accounts endpoint answers HTTP 500 for some entities (banks, funds, a few ordinary
   companies); recorded as `failed` for that field only. The frozen universe file is older than the live register
   (renames observed), so names always come from the register.
9. **Refresh is verified on replays and live reruns of the same companies,** not on real register changes (none occurred
   during development). The entity endpoint sends no ETag, so changes are found by value/content-hash comparison.
10. **Wall-clock cutoff is tested with a fake clock;** a real 45-minute run was never performed.

## Extra risks of the hiring / activity layer (unmeasured)
* A job listing is "listed on the company's own site", not verified against the posting's own page; stale listings
  stay stale. Page structure varies enormously; false negatives are expected, false positives are possible where a
  careers page contains links that look like postings (the context rule is the only guard).
* Date parsing is day-first for numeric dates (Norwegian). A site using month-first numeric dates would be misread.
* Up to 3 extra requests per website company (careers, feed or news): a verified-website company now costs up to 7
  requests (planner estimate 7, +1 for the optional LLM).

## Source rights
| source | use | terms |
|---|---|---|
| Enhetsregisteret API + bulk files (data.brreg.no) | identity, address, status, roles, workplaces | Norwegian Licence for Open Government Data (NLOD 2.0) |
| Regnskapsregisteret API (data.brreg.no) | annual accounts (only source of financial values) | NLOD 2.0; rate limits respected (filing-years endpoint throttled to ~28/min) |
| Company websites | only the website listed in the official register, only after the identity gate | robots.txt honoured (explicit disallow => `blocked`), 1 s per-domain throttle, max 4 requests per company, no login, no crawling beyond home + 2 pages |
| NVIDIA build / Google AI Studio (optional LLM) | verbatim text extraction from already-fetched, identity-verified pages | provider terms; keys supplied by the operator; no data is stored by us beyond the run output |

Not used: LinkedIn, Facebook/Instagram, Google/Bing result pages, Glassdoor, Indeed, search APIs, directories.
Person data: role holders' names and roles are public register data and are shown; birth dates and death flags are
never read or stored (scrubbed from recorded fixtures too). Contact mailboxes/phones are taken from the company's own
registered website; shared mailboxes (post@, info@ ...) come first and at most 3 emails / 2 phones are kept, but a named
colleague's work address can still appear when the site shows it in the company's own block.

## Dependencies and licences (pinned in `uv.lock`; read from installed package metadata)
beautifulsoup4 4.15.0 (MIT), extruct 0.18.0 (BSD), httpx 0.28.1 (BSD-3-Clause), lxml 6.1.3 (BSD-3-Clause),
pydantic 2.13.5 (MIT), pypdf 6.19.0 (BSD-3-Clause), tldextract 5.3.2 (BSD-3-Clause), trafilatura 2.3.0 (Apache-2.0);
dev: pytest 8.4.2 (MIT), ruff 0.16.10 (MIT). `kit/` is the Builderr starter kit, unmodified, imported as a library.

## Secrets
Keys are read only from environment variables / `.env` (git-ignored; `.env.example` has no values) and are sent only
in the `Authorization` header to the configured provider. A test asserts a key never appears in envelopes, the report
or the HTML even when the provider echoes it in an error body. Nothing is logged with credentials.

## Outbound URL safety
Public http(s) only. localhost/.local/.internal names, credentials in URLs, and any host that is or resolves to a
non-global address (private, loopback, link-local such as 169.254.169.254, reserved) are refused, again on every
redirect hop (max 3, re-validated). Response bodies are capped at 1 MB and must be HTML. Residual risk: DNS rebinding
between the check and the connection is not prevented. Hostile page text is never executed or rendered unescaped:
the HTML report escapes every value and only links http(s) URLs.

## External caches
`OUT/state.sqlite` (previous profiles for refresh, homepage content hashes) is the only persistent state; it is created
under the output directory and can be deleted. Bulk files are streamed, never written to disk.
