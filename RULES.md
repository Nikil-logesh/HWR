# Signalpost — participant brief

Status: Open. Round 1 runs from 23 August through 21 October 2026. Random daily evaluation begins 24 August.

## What to build

Build an agent that finds company information online.

Give it a Norwegian company number. It should search company websites, public registries and other permitted sources, then return a company profile with links to the facts it found. Check that each fact belongs to the right company, include its source and date, and clearly mark information you could not find. Run it again to keep the profile current.

## What to submit

Submit your agent's code, run instructions and a 100-company smoke-test result. You may use the public company list at any scale, but you do not submit precomputed profiles or a company manifest for scoring. The full submission checklist is below.

## How we test it

Builderr supplies an official company batch after the cutoff. Every eligible frozen entry receives the same current batch, including when the shared set grows from 1,000 to 1,100 companies. Your agent must handle company numbers it has not researched before.

## How you score

We combine independently checked findings from all submissions and Builderr's own crawlers into one reference collection. New verified findings update the collection, and every entrant is rescored against the same version. This is the checked information we have found, not a claim that we found everything online.

For each information type, 70% of its coverage score measures how many companies you covered and 30% measures how many individual facts you found. Example: the collection has 50 job postings across 20 companies. Finding 30 postings across 15 companies gives 60% of postings and 75% of companies: 70% × 75% + 30% × 60% = 70.5% for that information type. This feeds the 50 recall and coverage points; it is not the total score.

What to optimize: first make sure every fact belongs to the right company and has evidence. Then increase how much checked information you find. A high score cannot make up for a material wrong-company match.

The remaining points check whether each fact belongs to the right company and has a source (30), whether the profile gives useful supported explanations (12), and whether someone can find and verify the information (8). An entry qualifies with an official run and at least 65/100 overall. Coverage, recall and precision are scored dimensions, not separate qualification thresholds. Company-matching precision is separate from factual accuracy; fabricated financial values or a material wrong-company publication prevent the run from becoming official.

The exact requirements follow.

## What the company profile should show

The product should help someone understand a company before they apply, sell, partner or invest: what it does, who leads it, where it operates, how its latest filed numbers look, whether it appears to be hiring, and what dated public activity the checked sources reveal.

Your agent must find sources for the right company, show evidence for its facts and update the profile when the information changes.

## Universe and run format

- Universe: Norway-registered entities with observed official annual-account records.
- Public universe: all 411,160 eligible organisation numbers in the frozen 2025-filer snapshot.
- Local scale test: run your agent on 100 companies before submitting. You may test on 1,000 companies or more, but those outputs are not part of the score.
- Official evaluation: Builderr chooses the current shared company batch after the cutoff; every eligible frozen entry receives that same batch and must return one result per input.
- Completed runs add to a cumulative, locked checked reference set used when scores are updated.
- Daily schedule: the current shared company set per scheduled test day through 21 October; it is 1,000 companies now and may grow to 1,100.
- Builderr supplies organisation numbers, cutoff and output contract—not the companies' official sites or social identities.
- Every frozen submission receives the same batch and resource budget. A timeout or missing result is not scored; a Builderr infrastructure failure is rerun.
- Full public universe: [`signalpost-company-universe-2025.jsonl.gz`](../signalpost-company-universe-2025.jsonl.gz).
- Frozen eligible universe: 411,160 active entities whose latest submitted annual-account year was 2025. Uncompressed content SHA-256: `b82d6a3e7231d1759a958c282bc4366b80ec2fab8095053d8ed7fa9cd01bc838`. Download archive SHA-256: `1c89710e5b01f8617e86d09fbdff4a52f2f8dbbba297e74f7164b5984f5a0384`.

## Required company envelope

Every input must end in one terminal envelope, even when sources are missing or blocked.

Required sections:

1. Legal identity and public brand
2. Latest annual accounts and available history
3. Leadership and registered workplaces
4. Verified official website and company-owned profiles
5. Hiring and dated public activity from permitted sources
6. Claim-level evidence and availability state
7. Refresh metadata and material changes since the previous run

Use explicit states such as `available`, `not_available`, `blocked`, `not_applicable`, `ambiguous` and `failed`. Never turn absence into zero.

## Scoring — 100 points

Scoring version 2 applies to every Round 1 entrant from 26 August 2026. All active submissions are rescored under the same rubric and current pooled-evidence version.

- 50 — Recall and coverage: how much information did you find? For each information type, 70% measures company coverage and 30% measures individual facts found.
- 30 — Is the information correct? We check that each fact belongs to the right company and has a valid source and date.
- 12 — Is the summary useful? It should explain the company, changes and unknowns without making unsupported claims.
- 8 — Is it easy to use and verify? A user should be able to find, compare and verify the information on desktop and mobile.

For each external field family, its coverage score is 70% company recall and 30% individual-claim recall against the independently verified union of discoveries from every submitted crawler and Builderr’s own crawlers. The union grows when any agent contributes a new verified claim; each new version is hashed and every entrant is rescored against it. The final union freezes after final-submission verification.

Qualification requires an official run and 65/100. Coverage, recall and precision contribute to the score; they are not separate qualification thresholds. If the verified pool has fewer than 15 positive company-field opportunities across at least three external field families, recall is reported as not measured for that batch rather than as 0%. Final ranking uses the mean across every scheduled daily batch while your frozen version is active. An entrant-caused failed or missed batch scores zero after a clean reproduction; a Builderr harness, infrastructure or shared-source failure is void and rerun with the same code.

## Official run requirements

- Builderr supplies the current shared input set and a fixed time and resource budget for each official run.
- Return exactly one terminal envelope for every supplied company.
- If your agent times out or drops results, that run is not scored. A Builderr infrastructure failure is rerun.
- Your first submission is version 1; you may send up to four revised exact commit hashes by 18 October, for five versions total

## Official-run checks

- No fabricated financial values or material wrong-company publication
- Submitted public artifact includes a 100-company smoke-test result or report
- Exactly one terminal envelope for every company in each official batch
- Claim-level source, retrieval time and reporting period where relevant
- Honest availability states
- Idempotent refresh with prior snapshots preserved
- Reproducible setup, pinned dependencies and one evaluator command
- Declared source rights, server-side secrets and safe URL handling

Your score and qualification are separate. A small factual mistake lowers accuracy. A material wrong-company match can contaminate an entire profile, so the score remains visible but the run cannot become official until that match is corrected. It is better to miss some information than publish it under the wrong company; return `ambiguous` or `not_available` when the company match is uncertain.

## Rewards

- $2,000 main final pool: $1,200 / $500 / $300
- $500 JBOX bonus pool: $250 / $150 / $100
- Four separate $100 community-vote awards on 6 September, 20 September, 4 October and 18 October

Public voting does not alter the technical ranking. Only technically qualified agents enter the hosted gallery.

## Beyond the prize

The winning builder gets the opportunity to partner with [Håvard Liltved Dalen](https://www.linkedin.com/in/liltved/) to launch Signalpost in Norway. Håvard is a Norwegian serial entrepreneur, CPO at Fronted and co-founder of JBOX.

## Start here

Try one saved example first. Requires Python 3.12+; no API key or company-data download is needed.

```bash
curl -LO https://builderr.ai/signalpost-starter-kit.tar.gz
tar -xzf signalpost-starter-kit.tar.gz
cd signalpost-starter-kit
python3 scripts/run_refresh_replay.py \
  --manifest tests/fixtures/refresh-snapshots.json \
  --output out/refresh-demo.json
```

Open `out/refresh-demo.json` to inspect the changes and source evidence. This uses saved responses and does not qualify a competition entry.

Then follow `README.md` to install dependencies and try 100 live companies. It also explains how to test at larger scale; Builderr supplies the companies for official scoring.

- [Download the runnable reference agent](../signalpost-starter-kit.tar.gz)
- [Download the full 411,160-company universe](../signalpost-company-universe-2025.jsonl.gz)
- [Agent playbook](./signalpost-agent-playbook.md)
- [Learning harness](./signalpost-learning-harness.md)
- [Source policy](./signalpost-sources.md)
- [Evaluation contract](../docs/signalpost-evaluation-harness.md)
- [100-company product sample](https://builderr.ai/signalpost)

## Submit

Email `submit@builderr.ai` with the repository URL, exact commit hash, 100-company smoke-test result or report, one run command, models/APIs/licences, expected cost per official batch, agent name and contact for results.









# Signalpost agent playbook

This is the reference architecture, not a mandated framework. Keep any component only when a blind evaluation shows that it improves coverage without increasing wrong-company or unsupported-claim rates.

## 1. Start with authoritative identity

Seed every run with the organisation number, legal name, legal form, registered address, industry and latest filing year from Brønnøysundregistrene.

Treat the organisation number as the stable key. A brand, domain or social handle is only a candidate until it is tied back to the exact entity.

## 2. Resolve the public identity

Build an evidence graph rather than trusting name similarity:

`legal entity → official site candidate → public brand/aliases → leaders/founders → company profile candidate → reverse proof`

Useful proof includes the organisation number on the site, or a strong combination of legal name, address, phone, leadership and independent official evidence. Parent brands, franchises, sister companies and portfolio pages are not exact matches.

Leaders can help bridge a legal name to a public brand: find a verified role in the official register, locate the person's public profile through a permitted source, then confirm that the stated company resolves back to the same entity. This generates candidates; it does not replace exact-entity verification.

## 3. Crawl deterministically first

A practical baseline:

- Scrapy for queues, throttling, retry, deduplication and per-domain budgets
- Sitemap and static HTML before browser rendering
- extruct for JSON-LD, OpenGraph and microdata
- Trafilatura for readable page text
- Playwright only when a deterministic check identifies a JavaScript shell
- Pydantic or an equivalent typed validator before publication
- Plain PDF text extraction first; layout/OCR only for difficult annual reports

Prioritise `/about`, `/om-oss`, `/contact`, `/kontakt`, `/leadership`, `/ledelse`, `/locations`, `/careers`, `/jobs`, `/news` and `/investor`.

## 4. Use a source ladder

1. Official registers and annual accounts
2. Verified company-owned sites and feeds
3. Official or licensed platform APIs
4. Permitted public pages with recorded terms and provenance
5. Search/discovery providers for candidate generation only

Never use search rank or an unofficial scraper response as the evidence for a published fact. Re-fetch the underlying permitted source and preserve it.

## 5. Preserve evidence before extraction

Store immutable raw snapshots with:

- requested and final URL
- redirect chain and response status
- retrieval timestamp and relevant effective/reporting date
- content hash
- parser and extractor version
- source class and access policy

Every published claim should point to a snapshot plus a selector, character span, table cell or PDF page.

## 6. Extract in layers

Run structured data first, DOM attributes second, clean text third, deterministic role/location rules fourth, and model extraction last. Validate every output. Retain conflicting candidates rather than silently choosing one.

An LLM may summarise supported claims or propose candidates. It must not decide exact identity, invent a missing field, or silently override deterministic evidence.

## 7. Refresh as a diff

Use stable claim keys, immutable snapshots and idempotent upserts. A refresh produces:

- current supported value
- previous supported value
- first and last observed timestamps
- change type and materiality
- sources supporting both sides of the change

Re-crawl by source volatility: official annual accounts slowly; jobs and company news more frequently. Failed refreshes keep the last known supported value and expose the failure.

## 8. Evaluate as a control loop

Freeze development, validation and final sets with no organisation or host overlap. Hand-label exact identity, claim support and expected availability. Tune only on development, set thresholds once on validation and run the final set once.

Track:

- exact-company precision and wrong-company publications
- field precision, recall and coverage
- evidence-span validity
- static and browser-rendered crawl success
- refresh correctness and false-change rate
- cost, requests and p50/p95 time per company

Abstention is allowed and must be reported. It cannot be used to hide low coverage.

## 9. Suggested repository files

- `README.md` — setup and evaluator command
- `AGENT.md` — research and abstention policy
- `CRAWLERS.md` — connectors, budgets and fallback rules
- `IDENTITY_RESOLUTION.md` — candidate and publication gates
- `DATA_SCHEMA.md` — envelopes, claims and evidence
- `REFRESH.md` — scheduling, snapshots and diffs
- `EVAL.md` — corpus split, metrics and thresholds
- `LIMITATIONS.md` — known gaps, licences and source restrictions

## Non-negotiable limitation

LinkedIn, Meta, Glassdoor, Indeed and similar platforms have access restrictions. Use only official, licensed or otherwise permitted access. Open-source or unofficial clients may be evaluated in a private experiment, but they do not make prohibited collection permissible and cannot be the sole support for a published claim.


## Common traps

Most entries that cannot be scored fail here rather than on the research.

**Your agent picks its own companies.** We hand it the official company batch at run time, chosen after the daily cutoff. Some will be companies you have never seen. Read them from that file. An agent working from its own list cannot be scored, however good the research is.

**It handles one company at a time.** We need a batch: 100 company numbers in, 100 results out, from one run. This is usually a wrapper around what you already have rather than a rewrite.

**There is no single command to run it.** Give one command that can be pasted. A list of steps or a notebook cannot be run automatically.

**It does not install on a clean machine.** Clone your own repository into a new folder at the pinned commit, make an empty virtual environment, run only your declared install step, then your run command. That check matches ours and catches packages you installed months ago and forgot about.

**It returns fewer than 100 results.** Every company comes back, including the ones you found nothing for. Each result carries one of `available`, `not_available`, `blocked`, `not_applicable`, `ambiguous` or `failed`. If we hand you 100 and 60 come back, we cannot tell whether the rest were blocked, empty or crashed, so the run cannot be scored. "I found nothing" is a valid answer. A missing row is not. Never return zero in place of missing information.

**You think you cannot use an LLM.** You can. Each run has a small external API budget, and if you need a model key for scoring, ask and we will supply one. What we cannot use is a credential tied to your own account on another service, because we cannot reproduce your run with it.



















# Signalpost source policy

The competition rewards useful discovery only when the resulting evidence is lawful, reproducible and attributable to the exact company.

## Preferred sources

### Official Norwegian records

- Brønnøysundregistrene Enhetsregisteret bulk data and entity API for identity, legal form, address, industry and registered employee count
- Regnskapsregisteret API and annual-account copies for filed financial data and history
- Official roles endpoints for management and board roles
- Official subunit records for registered workplaces

Official data is the identity anchor. It does not, by itself, identify the public brand or website.

### Company-owned sources

- Verified official website
- Sitemap, news, investor, careers, location and contact pages
- Structured data embedded by the company
- Social or video profiles linked by the verified company site, subject to the destination platform's access terms

### External sources

- Official or licensed platform APIs
- Search APIs used to discover candidates
- Public pages whose terms and robots policy permit the submitted access pattern
- Licensed news, review, jobs, traffic or company-data feeds

## Publication rules

- Search results generate candidates; they are not claim evidence.
- A profile or domain must resolve to the exact legal entity before its facts are published.
- Group, parent, subsidiary, franchise and public-brand relationships must be labelled, not collapsed.
- Every claim records source URL or source identifier, retrieval time, effective/reporting date where relevant, content hash and extraction method.
- Missing, blocked and ambiguous are explicit states.
- Company-owned promotional copy may describe the business but cannot provide an independent sentiment claim.

## Restricted platforms and unofficial crawlers

Do not scrape a platform when its terms, robots policy or applicable law prohibit the submitted method. This includes treating unofficial LinkedIn, Meta, Glassdoor, Indeed or Google clients as automatically acceptable simply because code exists on GitHub.

An unofficial connector may be tested privately as a candidate-discovery experiment. For competition scoring, the entrant must declare the connector, demonstrate permitted access and independently verify any published claim from a durable permitted source.

## Evidence beats volume

The competition does not reward request count, pages downloaded or raw posts collected. It rewards exact-company, decision-useful coverage with valid evidence and reproducible refresh behavior.














# Signalpost learning harness

The winning system should improve through measured experiments, not through vague self-reflection. A simple evaluation loop is enough:

`try a strategy → preserve the attempt → score it → compare it → promote or reject it`

The public development set is training ground. Hidden companies are the exam.

## 1. Create a strategy registry

Give every discovery or extraction route a stable name and version. Start with:

- registry-provided website
- sitemap and robots discovery
- static homepage crawl
- targeted `/about`, `/contact`, `/leadership`, `/locations`, `/careers` and `/news` paths
- JSON-LD and OpenGraph extraction
- search-provider candidate discovery
- leader/founder bridge from official role to public brand
- browser-rendered fallback for a confirmed JavaScript shell
- annual-account PDF fallback

Do not let the agent silently invent and deploy new production code. New strategies enter the registry, run on the development set and face the same tests as the current winner.

## 2. Save every attempt

For every company and strategy, record:

- strategy name and version
- input organisation number
- requested URLs and redirect chain
- raw snapshot hashes
- candidate domains, profiles and claims
- accepted and rejected claims with reasons
- exact-identity evidence
- runtime, request count and cost
- errors and availability states

This makes failures useful. You can see whether a strategy found nothing, chose the wrong company, extracted bad data or simply cost too much.

## 3. Score in the right order

Use a hand-reviewed public gold set. Score each strategy in this order:

1. Wrong-company publications — must not increase
2. Supported-claim precision — must not fall
3. Evidence validity — every accepted claim points to the right source span
4. Coverage and recall — useful supported fields added
5. Refresh correctness — real changes found without false changes
6. Runtime, requests and cost

A strategy that finds more data about the wrong company loses.

## 4. Use a strict promotion rule

Promote a challenger only when all are true:

- zero new material wrong-company publications
- no meaningful drop in claim precision
- evidence completeness remains 100% for published material claims
- useful coverage or recall improves by a declared minimum
- runtime and cost remain within budget

Keep the previous strategy available for rollback. Store the decision and the exact evaluation report.

For the first version, use a decision table rather than reinforcement learning. Example: static HTML first; browser rendering only after a JavaScript-shell test; PDF layout parsing only when plain text fails. A contextual bandit or learned router is optional later, after enough labelled attempts exist.

## 5. Separate learning from refresh

Learning chooses better strategies. Refresh revisits evidence with the chosen frozen strategies.

A refresh should preserve the previous value, store the new snapshot and emit a typed change such as `new_role`, `closed_job`, `new_location`, `new_filing` or `changed_description`. A failed refresh must not erase the last supported value.

## 6. Freeze before daily evaluation

Before Builderr selects the next random daily batch, freeze:

- code and dependency lockfile
- strategy versions and routing table
- prompts, models and model versions
- thresholds and publication gates
- source allowlist and budgets

Operational retries may follow the frozen policy. Hidden scores and labels must not tune the running submission.

## Recommended starter repositories

### Core crawl and extraction

- [Scrapy](https://github.com/scrapy/scrapy) — queues, throttling, retries, deduplication and crawl budgets
- [scrapy-playwright](https://github.com/scrapy-plugins/scrapy-playwright) — browser fallback for pages that truly require JavaScript
- [extruct](https://github.com/scrapinghub/extruct) — JSON-LD, microdata, RDFa and OpenGraph extraction
- [Trafilatura](https://github.com/adbar/trafilatura) — readable text and metadata extraction
- [Pydantic](https://github.com/pydantic/pydantic) — typed company, claim and evidence envelopes

### Identity and normalization

- [RapidFuzz](https://github.com/rapidfuzz/RapidFuzz) — fuzzy candidate matching after organisation-number checks
- [tldextract](https://github.com/john-kurkowski/tldextract) — registered-domain normalization
- [phonenumbers](https://github.com/daviddrysdale/python-phonenumbers) — phone normalization and corroboration

### Documents and difficult pages

- [pypdf](https://github.com/py-pdf/pypdf) — fast first pass for text PDFs
- [Docling](https://github.com/docling-project/docling) — tables and layout-heavy reports when the simple pass fails
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) — scanned pages only

### Evaluation and storage

- [pytest](https://github.com/pytest-dev/pytest) — regression and connector tests
- [DuckDB](https://github.com/duckdb/duckdb) with Parquet — local attempt analysis and benchmark reports
- [OpenTelemetry Python](https://github.com/open-telemetry/opentelemetry-python) — runtime traces; keep claim provenance in product tables

### Optional connector experiments

- [JobSpy](https://github.com/speedyapply/JobSpy) can help benchmark job discovery across several platforms.
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) can help test public video metadata discovery.

These are experiments, not automatic permission to collect. The submitted access method must comply with source terms and applicable law. Prefer official or licensed APIs, and independently verify every published company claim.

## Smallest useful repository layout

```text
strategies/
  registry_site.py
  sitemap_static.py
  search_candidates.py
  browser_fallback.py
  pdf_fallback.py
eval/
  gold_companies.jsonl
  score_attempts.py
  promotion_gate.py
snapshots/
claims/
reports/
```

One command should run the public loop and produce a comparison report:

```bash
python -m eval.run --corpus eval/gold_companies.jsonl --challenger browser_fallback_v2
```










# Signalpost evaluation contract

Status: scoring version 2, effective 26 August 2026 for every Round 1 entrant. Random daily evaluation began 24 August; all active submissions are rescored under version 2.

## In plain language

Build a program that researches companies and keeps their profiles current. Test it locally on 100 companies; Builderr supplies the official company batch for scoring and gives the same current batch to every eligible frozen entry.

We combine independently checked findings from all submissions and Builderr's own crawlers into one reference collection. New verified findings update the collection, and every entrant is rescored against the same version. This is the checked information we have found, not a claim that we found everything online.

For each information type, 70% of its coverage score measures how many companies you covered and 30% measures how many individual facts you found. Example: the collection has 50 job postings across 20 companies. Finding 30 postings across 15 companies gives 60% of postings and 75% of companies: 70% × 75% + 30% × 60% = 70.5% for that information type. This feeds the 50 recall and coverage points; it is not the total score.

The remaining points check precision and evidence (30), useful explanations (12) and ease of use (8). An entry qualifies with an official run and at least 65/100 overall. Coverage, recall and precision are scored dimensions, not separate qualification thresholds. Company-matching precision is separate from factual accuracy; fabricated financial values or a material wrong-company publication prevent the run from becoming official.

The exact requirements follow.

## Corpus

- Universe: Norway-registered entities with observed annual-account records.
- Public universe: all 411,160 eligible organisation numbers.
- Local scale test: 100 companies. Larger local tests, including 1,000 or more companies, are encouraged but their precomputed profiles are not submitted or scored.
- Public product sample: 100 profiles at `/signalpost`.
- Official evaluation: Builderr selects the current shared batch after each cutoff; every eligible frozen entry receives the same batch. The shared set may grow—for example, from 1,000 to 1,100 companies—and all active entries are run on the same expanded set.
- Completed runs add to a cumulative, locked checked reference set used when scores are updated.
- The public universe is available for local testing. Freshness, exact attribution and reproducible execution—not a submitted static profile file—are what the official run tests.
- Every entrant receives the same batch, cutoff, network policy and resource budget. A timeout or missing result is not scored; a Builderr infrastructure failure is rerun.
- Eligible-universe uncompressed content SHA-256: `b82d6a3e7231d1759a958c282bc4366b80ec2fab8095053d8ed7fa9cd01bc838`.
- Public `.jsonl.gz` archive SHA-256: `1c89710e5b01f8617e86d09fbdff4a52f2f8dbbba297e74f7164b5984f5a0384`.

## Output contract

Exactly one terminal envelope per input organisation number. Envelopes must contain legal identity, claims, evidence references, availability states, source snapshots, refresh metadata and errors. Valid states are `available`, `not_available`, `blocked`, `not_applicable`, `ambiguous` and `failed`.

## Scoring — 100

1. Recall and coverage — 50
2. Precision, exact identity and evidence — 30
3. Decision-useful synthesis — 12
4. UX and interaction — 8

Recall and coverage control 50 points. For every external field family, coverage is 70% company recall and 30% individual-claim recall against the independently verified union of discoveries from every submitted crawler and Builderr’s own crawlers. The union is cumulative and versioned: each verified addition creates a new pool hash and every entrant is rescored against that same latest version. The final union freezes only after all eligible final submissions have been verified.

## Official-run checks
- The submitted public artifact includes a 100-company smoke-test result or report.
- Every official input produces exactly one terminal envelope per company.
- No fabricated financial value or material wrong-company publication.
- Published material claims have source, retrieval time and reporting period where relevant.
- Missing values are never silently converted to zero.
- Re-running the same snapshot is idempotent.
- Refresh preserves prior evidence and exposes material changes.
- Setup is reproducible with pinned dependencies and one evaluator command.
- Source rights, secrets and outbound URL policy are documented and safe.

Qualification is an official run with 65/100 or more. Official-run checks establish whether the run is valid; they do not create additional score bars. Final ranking uses the mean across every scheduled daily batch while an entrant has an active frozen version. An entrant-caused failed or missed batch scores zero after Builderr reproduces the failure in a clean evaluator run. A batch affected by Builderr's harness, infrastructure or a shared-source failure is void and rerun for every affected entrant with the same frozen code. Ties break on fewer wrong-company publications, then higher weighted company recall, then lower declared third-party cost.

## Official run requirements

- The current official input batch, supplied by Builderr (1,000 companies now; it may grow to 1,100)
- A fixed time and resource budget supplied equally to every entrant
- Exactly one terminal envelope for every input company
- A timeout or missing result is not scored. A Builderr infrastructure failure is rerun for every affected entry.
- server-side secrets supplied through documented environment variables only

Builderr provides the frozen official registry snapshot used for identity anchoring. External caches must be declared. Cached public-universe material is allowed, but the official score still enforces source timestamps, refresh behavior and the same evidence cutoff for everyone.

The first submission is version 1. Entrants may then submit up to four revised exact commit hashes, for five versions total. Revisions close 18 October 2026, take effect only after being frozen for the next daily run, and never replace earlier batch results.

If the verified pool has fewer than 15 positive company-field opportunities across at least three external field families, recall is reported as not measured for that batch rather than as 0%. It remains a scored observation, not a qualification gate.

## Measurement

Report exact-company precision, wrong-company publications, per-field precision/recall/coverage, evidence-span validity, crawl completion, refresh correctness, false-change rate, cost per company, request count, and p50/p95 runtime. Abstention is reported separately and cannot satisfy coverage.

## Public voting

Only qualified entries enter the hosted Builderr gallery. A $100 public-vote award runs every fortnight. Votes never alter the final technical score or ranking.

## Local checks

```bash
npm run check:signalpost
npm run check:signalpost-showcase
npm run check:signalpost-challenge
```










and event information in website-->
Open for entries
company research
Build an agent that finds company information online.
Give it a Norwegian company number. It finds public facts, links each fact to a source, and keeps the profile current.
Prize
$2,500 final rewards
Closes
Oct 21
Scored on
50 recall · 30 precision · 12 synthesis · 8 UX
Benchmark
Same checked company collection
1Build
Use the starter brief.
2Submit
Send one version of your code.
3Test
We run the same published test.
4Score
The metric below sets your rank.
Download the runnable starter ↓
How scoring works →
Download the brief, run a sample, then follow the submission steps below.Download starter brief ↓

Public board

Current standings
open
Signalpost · open
Ends Oct 21
Public universe
411,160 companies
Submit
1,000+ profiles
Qualify
65/100 on a verified run
28 submissions · 17 assessed · 0 qualified
Reviewed 1 October 2026. Each scored entry ran twice on the same locked 1,200-company set. Entries without a reproducible, evidence-complete run do not receive a board score. No entry reached 65/100, and no winner has been declared.

#	Builder and score breakdown	Result
1	Karthik
Recall 17.86/50
Evidence 18.93/30
Synthesis 7.20/12
UX 1.60/8
45.59/100
Not qualified
2	Hardik
Recall 13.96/50
Evidence 18.92/30
Synthesis 7.20/12
UX 3.20/8
43.28/100
Not qualified
3	Ajai
Recall 13.60/50
Evidence 18.92/30
Synthesis 7.20/12
UX 3.20/8
42.92/100
Not qualified
4	Vishwajit
Recall 12.97/50
Evidence 18.92/30
Synthesis 7.20/12
UX 3.20/8
42.29/100
Not qualified
5	Devansh
Recall 12.94/50
Evidence 18.92/30
Synthesis 7.20/12
UX 3.20/8
42.26/100
Not qualified
6	Dhanush
Recall 12.89/50
Evidence 18.92/30
Synthesis 7.20/12
UX 3.20/8
42.21/100
Not qualified
6	digikuo
Recall 12.89/50
Evidence 18.92/30
Synthesis 7.20/12
UX 3.20/8
42.21/100
Not qualified
6	Harsh
Recall 12.89/50
Evidence 18.92/30
Synthesis 7.20/12
UX 3.20/8
42.21/100
Not qualified
6	Navadeep
Recall 12.89/50
Evidence 18.92/30
Synthesis 7.20/12
UX 3.20/8
42.21/100
Not qualified
6	Sanjai
Recall 12.89/50
Evidence 18.92/30
Synthesis 7.20/12
UX 3.20/8
42.21/100
Not qualified
11	Penge
Recall 12.94/50
Evidence 18.92/30
Synthesis 7.20/12
UX 1.60/8
40.66/100
Not qualified
12	Jaydatt
Recall 12.89/50
Evidence 18.92/30
Synthesis 7.20/12
UX 1.60/8
40.61/100
Not qualified
13	Sudhir
Recall 12.89/50
Evidence 14.92/30
Synthesis 7.20/12
UX 3.20/8
38.21/100
Not qualified
14	Krishi
Recall 0.00/50
Evidence 0.00/30
Synthesis 4.80/12
UX 1.60/8
6.40/100
Not qualified
14	Martyn
Recall 0.00/50
Evidence 0.00/30
Synthesis 4.80/12
UX 1.60/8
6.40/100
Not qualified
14	Rakesh
Recall 0.00/50
Evidence 0.00/30
Synthesis 4.80/12
UX 1.60/8
6.40/100
Not qualified
14	Rewas
Recall 0.00/50
Evidence 0.00/30
Synthesis 4.80/12
UX 1.60/8
6.40/100
Not qualified
Qualification requires 65/100 on an official run. The score is 50 recall and coverage, 30 precision and evidence, 12 synthesis, and 8 UX. How scoring works →

Start with the Python example and company list. Improve what it finds, the sources it shows, and how it updates profiles.
Download code ↓
Get all 411,160 ↓
Build and submit →
First run: one saved company, about 5 minutes. No API key or company download. This is practice, not an entry. Download the starter → View the sample site → Send a blocker →

01 · What to build

Find the information. Get it right.
Build a company research agent. Collect company details, people, locations, financial results, jobs and public activity where available.

Check each fact belongs to the right company. Link it to its source and date. Clearly mark anything you could not find.

Keep profiles current. Check sources again, show what changed and preserve the earlier evidence.

Your starting list: 411,160 eligible Norwegian companies with 2025 annual-account records. Your agent must work from a company number, including companies it has not researched before.

02 · What to submit

Submit your agent and a 100-company smoke test.
A 100-company smoke-test result or run report showing that your agent returns one complete result per input.
Your repository link, exact commit hash and one command to run the agent.
The models, APIs and licences you use, expected cost per official run, and contact details.
Use the public company list to test at any scale, including 1,000 companies or more. You do not need to submit precomputed profiles or a company manifest. Builderr supplies the companies for every official run.

Submit to Builderr →
03 · How we test it

The same official company batch for every eligible entry.
Builderr chooses the official company batch after the cutoff and gives the same batch to every eligible entry. The current shared set can grow over time—for example, from 1,000 to 1,100 companies. When it grows, every active entry is run on the same current set.

Your local 100-company smoke test is only for checking that your code works. It is not your competition score, and your precomputed profiles are not used for ranking. We score the agent on the fresh companies Builderr supplies.

Each official run has a fixed time and resource budget. Finish the run and return one result for every supplied company. If your agent times out or drops results, that run is not scored. If Builderr’s infrastructure fails, we rerun it.

04 · Common traps

Most failed runs fail here, not on the research.
Your agent picks its own companies. We hand it the official company batch at run time, chosen after the daily cutoff. Some will be companies you have never seen. Read them from that file. An agent working from its own list cannot be scored, however good the research is.

It handles one company at a time. We need one result per company in the batch, including when the official batch grows beyond 100 companies.

There is no single command to run it. Give us one command we can paste. A list of steps or a notebook cannot be run automatically.

It does not install on a clean machine. Clone your own repository into a new folder at the pinned commit, make an empty virtual environment, run only your declared install step, then your run command. That check matches ours and catches packages you installed months ago and forgot about.

It returns fewer than 100 results. Every company comes back, including the ones you found nothing for. See the result envelope below.

You think you cannot use an LLM. You can. Each run has a small external API budget, and if you need a model key for scoring, ask and we will supply one. What we cannot use is a credential tied to your own account on another service, because we cannot reproduce your run with it.

05 · How you score

Find more facts. Keep them accurate and current.
What to optimize: first make sure every fact belongs to the right company and has evidence. Then increase how much checked information you find. A high score cannot make up for a material wrong-company match.

50
points
Recall and coverage: how much did you find?
We compare every agent with the same checked collection. 70% measures how many companies you covered and 30% measures how many checked facts you found.

30
points
Is the information correct?
We check that each fact belongs to the right company and has a valid source and date. Wrong or unsupported facts lose points. A material wrong-company match also blocks qualification.

12
points
Synthesis: is the result useful?
The profile should explain what the company does, what changed and what remains unknown, with sources for its conclusions.

8
points
UX: is it easy to use and verify?
We check whether a user can find, compare and verify company information on desktop and mobile.

How do we know how much you found?
We combine findings from all submissions and Builderr’s own crawlers. We check the sources, remove duplicate facts and wrong-company matches, then compare everyone against that same collection.

For each type of information, 70% of its coverage score comes from how many companies you covered; 30% comes from how many individual facts you found.

Example: our checked collection has 50 job postings across 20 companies. You find 30 postings across 15 of those companies. That is 60% of postings and 75% of companies.

70% × 75% + 30% × 60% = 70.5% for this information type.

This feeds the 50 recall and coverage points, not your total score. Precision and evidence, synthesis, and UX make up the remaining 50 points. New verified findings update the collection and everyone’s scores. We finalize it after checking all eligible final submissions; it is not a claim that we found everything online.

06 · Qualification

Meet the score bar on an official run.
At least 65/100 overall on an official run.
Recall and coverage (50), precision and evidence (30), synthesis (12), and UX (8) make up the score. They are not separate qualification thresholds.
Return a result for every company Builderr supplies, including when information is missing or blocked. Never replace missing values with zero.
Keep the source, retrieval date and relevant reporting period for every claim. Preserve earlier evidence and avoid duplicate records when rerunning.
Unsafe source or secret handling, fabricated claims, compromised evidence, and evaluator failures are investigated with named ownership. A Builderr harness or shared-source failure is rerun and is not assigned to the builder.
Your score and qualification are separate.
A small factual mistake lowers your accuracy. A material wrong-company match is more serious because it can put an entire website, brand and set of facts under the wrong profile. Your score remains visible, but the run cannot become official until that match is corrected.

It is better to miss some information than publish it under the wrong company. When the company match is uncertain, return ambiguous or not available instead.

Return a result for every company.
We hand your agent a company batch and need one result per input, including the ones you found nothing for. Each result carries one of these states:

available — you found it
not_available — you looked, there is nothing there
blocked — the source refused the request
not_applicable — the question does not apply to this company
ambiguous — you could not be sure it is the right company
failed — the run broke on this one
If we hand you a batch and some results are missing, we cannot tell whether the rest were blocked, empty or crashed, so the run cannot be scored. “I found nothing” is a valid answer. A missing row is not.

Every official run: finish within the supplied time and resource budget, and return one result for every company. A timeout or missing result means that run is not scored; a Builderr infrastructure failure is rerun.

How we rank qualified entries: We average every scheduled daily batch while your submitted code is active. If your code fails or misses a batch after a clean evaluator rerun, that batch scores zero. A Builderr harness, infrastructure or shared-source failure is void and rerun with the same code. Ties go to fewer wrong-company facts, then better company coverage, then lower third-party API cost.

Full technical requirements and final ranking
Each official run has a fixed time and resource budget. Builderr supplies the company batch and output format for the run.

Return exactly one terminal result envelope for every input company. Use distinct available, not_available, blocked, not_applicable, ambiguous and failed states. Refresh must be idempotent: the same source snapshot must not create duplicate records or false changes.

External company recall and exact-company precision contribute to the score. A sparse batch is scored only on the evidence available for that batch; it does not create a new qualification threshold.

Exact tiebreak order: fewer wrong-company publications, then higher weighted company recall, then lower declared third-party cost. Document source rights, server-side secrets and safe URL handling. Supply pinned dependencies and one reproducible run command. Integrity, evidence and operational requirements in the evaluation contract still apply.

Your first submission is version 1. You may then submit up to four revised commit hashes before Oct 18, for five versions total. Each revision is frozen before its next official run and applies only to later batches. The evaluation contract contains the exact scoring terms and run format.

07 · Rewards

$2,500 in final prizes.
Main challenge — $2,000: $1,200 / $500 / $300 for first, second and third.

Separate JBOX bonus — $500: $250 / $150 / $100 for qualifying agents built with JBOX.

Community awards — $100 × 4: Sep 6, Sep 20, Oct 4 and Oct 18. Public voting never changes the technical ranking.

Only qualified entries enter the hosted Builderr gallery. Builderr covers hosting during the competition.

The winning builder gets the opportunity to partner with Håvard Liltved Dalen to launch Signalpost in Norway. Håvard is CPO at Fronted and co-founder of JBOX.