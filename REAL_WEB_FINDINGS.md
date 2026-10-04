# What happened when the web layer met real websites

Run on 2026-10-04 from the build sandbox against **150 real Norwegian companies whose register entry lists a website**
(`samples/websites150.jsonl`, seeded from the frozen universe), no LLM (`--no-llm`), live fetches with robots.txt honoured
and a 1 s per-domain throttle. Result files: `reports/real-web-150/` (`envelopes.jsonl`, `report.json`, `web_report.md`,
`audit_sheet.md`, `audit_flags.json`). This is **one sample of 150**, not an estimate with error bars.

## Numbers (final code, live run, 305 s, 1,146 requests = 7.6 per company, $0)
| `official_website` outcome | Companies |
|---|---|
| verified (`available`) | **48** (32%) |
| `ambiguous` (identity not proven, nothing from the site published) | 68 |
| `failed` (fetch failed) | 28 |
| `blocked` (robots.txt) | 4 |
| `not_available` (HTTP 404 / no website) | 2 |

Why the 68 were not published: 33 legal name not on the page, 25 page names a different organisation number, 9 only the
name (0.50) or name + municipality (0.70), 1 portfolio page listing other companies. The 28 failures are mostly dead or
unreachable domains (14 `ConnectError`, 4 `ConnectTimeout`, 1 `ReadTimeout`) plus 6 `ProxyError`; **I cannot say how many
of those are the sandbox's egress proxy rather than the site** — plain `http://` URLs were refused with 403 here, so
some failures may not reproduce from another network.

Facts on the 48 verified sites: description 27, email 40, phone 45, LinkedIn 8, Facebook 11, Instagram 7, careers page 8,
dated activity 8, `no_open_positions` statement 1, **open job listings 0, products/services 0** (needs the LLM).
A replay of the recorded pages through the same code gave the same claims for 148 of 150 companies; the other 2 differ
only in `failed` vs `ambiguous` (transient fetch results).

## What a human check found, and what changed
The first real run reported 43 verified sites and **the automated audit raised 0 flags**. Reading the evidence of each
verified site by hand found real defects the audit cannot see (it only checks names/ids). All were fixed in code, each with
a regression test built on synthetic text (`tests/test_contact_precision.py`, `test_identity_partial.py`,
`test_identity_group.py`, `test_signals.py`):

| Defect seen on real sites | Fix |
|---|---|
| A date `30.04.2026` published as a phone number | no dots/dashes inside numbers; a date-parse check |
| `+46` (Swedish) and `+45` (Danish) numbers published as Norwegian; `+ 47 90 76 50 80` cut to a *different* 8-digit number | foreign country codes rejected; `+ 47` handled; a number followed by more digit groups is not a number |
| The same phone listed twice in two spacings | one fact per 8-digit number |
| Template (`fornavn.etternavn@…`), no-reply, invoicing (`faktura@`, e-invoice inbox), third-party (invoice-scanner, property-manager) mailboxes as the company's email | rejected; mailboxes on another domain need the company's name in the domain (home TLDs only) or in the same text block |
| Personal mailboxes crowding out `post@` under the cap | shared mailboxes first |
| A kindergarten chain's page gave the phone of a **sister kindergarten** and the chain's administration mailboxes | contacts are tied to the unit block (full legal name / street / postcode / org number) that precedes them; on a page with a block for the company only that block counts; on a multi-location page with none, nothing is published |
| A subsidiary's page on its parent's contact page gave the **group's** mailboxes | same rule (the subsidiary's own block is found by its full legal name, not by the shared brand) |
| A property group's page listing 8 single-purpose companies with their org numbers verified one of them | a page naming ≥ 2 other entity-labelled organisation numbers is a group/portfolio page → `ambiguous` (RULES.md: portfolio pages are not exact matches) |
| An address block, or text with `<br />`, published as the website description | rejected |
| `© 2026` and phone fragments counted as postcodes | excluded from address detection |
| Tracking parameters (`?view_public_for=…`) inside social URLs | stripped from the value; the snippet keeps the link as published |
| "Slik jobber vi" (*how we work*) blog post taken for the careers page | `jobbe` only matches as a word |
| Correct sites rejected because the page abbreviates the legal name (`Smørhamn Handelsstad` vs `SMØRHAMN HANDELSTAD AS`) | new 0.90 tier: a distinctive name word + exact street *with number* + postcode and city together; a labelled different org number still vetoes |
| `www.` vs apex host failing to connect | on a transport error the other form of the host is tried once (robots re-checked) |
| Org number found but the registered name appears nowhere (`Scala Bø AS` vs a page naming another company next to that number) | still published but scored 0.95 with signal `legal_name_not_on_page`, so it is visibly less certain |

After the fixes: 48 verified sites; no company lost its only phone or email; 6 gained an email; 184 contact candidates
(counted per page: person-level numbers and mailboxes away from the company's own block) are now dropped — that is the
price of the unit-block rule and it is intentional.

## What is still uncertain (do not read these as measured precision)
* **Not a precision estimate.** I read 48 sites' contact, description and social values against their snippets; I did
  not open every page in a browser. Two reviewers would likely disagree on a few borderline cases (e.g. a clinic inside
  a shared medical centre publishing the centre's mailbox is no longer published, but a branch's phone on the same page
  may be).
* **Chain/association sites remain the hardest case.** `SKEISBOTNEN BARNEHAGE AS` is verified through `piba.no` (a
  four-kindergarten chain) because its own name, street and postcode appear there; its contacts are now limited to its
  own block, but its careers page is the chain's. The explanation says where each fact came from.
* **`SCALA BØ AS` / `bosenteret.no`:** the page pairs this organisation number with a different company name
  ("Fredriksborg Eiendom AS"). I could not tell whether the site is stale or wrong; it is published at 0.95 with the
  flag above. A reviewer may prefer to drop it.
* **Hiring:** 8 careers pages were found; **0** contained a recognised job listing. One said "no open positions"; one
  (a school) linked to an external NAV posting for a position starting 1 February 2026 — not published (anchor without
  listing context, and stale). The extractor is conservative by design; whether real postings would be recognised is
  **untested on a real posting** (no site in this sample produced a recognised posting).
* **Dated activity** (8 sites) comes from WordPress RSS feeds; I spot-checked the reported titles and dates against their
  feed snippets for the sites in the report sample (7 of the 8), not all items. Evidence snippets are raw feed XML slices —
  literal but not pretty.
* **Recall is bounded by the register.** Only ~11% of companies list a website; this sample was *chosen* from those that
  do, so 150/150 is not representative of an official batch.
* **Replay is not live.** The recorded pages (`page_cache/`, not committed) let me iterate offline; the final numbers above
  are from a fresh live run, which agreed with the replay.
* The `ProxyError`/`http://` observations above are specific to this sandbox.

## Why recall is still low, and what I did not do
Strictness is the main cost: 68 ambiguous sites. About 55 of them looked like correct rejections on manual reading
(manager/chain/group sites naming other organisations; pages with no trace of the company); about 4 were clear false
negatives (the new tier verifies 2 sites in this sample); the rest were unclear. I did **not** loosen the gate to chase
the recall number, because RULES.md ranks a wrong-company publication above a missing fact.

## With the LLM on (same 150 sites, same recorded pages, 2026-10-04)
`google/gemma-4-31b-it` on the NVIDIA free tier (the only model that met the benchmark thresholds), JSON mode, verbatim
spans only, every snippet checked by code. Result files: `reports/real-web-150-llm/`.

| | no LLM | LLM |
|---|---|---|
| verified sites / identity decisions | 48 | 48 (the LLM never decides identity; unchanged) |
| `website_description` | 27 | **45** |
| `products_services` | 0 | **44** |
| LLM calls / failures | 0 | 48 / 1 |
| tokens (prompt / completion) | 0 | 73,264 / 10,649 |
| wall clock for the 150 | 66 s (replay) | **638 s** |
| third-party cost | $0 | $0 (free tier, declared) |

I read all 62 LLM-published facts against their snippets. All are literal page text and about the right entity. Weak spots:
* **Chain pages:** `SKEISBOTNEN BARNEHAGE AS` gets the Pioner chain's sustainability sentence as its description and the
  four kindergartens' names as "services". The page is the chain's; the text is not specific to this company.
* **Low-value services:** `RESIDENTIAL`/`COMMERCIAL` (Krista Hartmann), department names as services (Brøttet Barnehage),
  events (Kongsberg Jazzfestival), job titles (Blokksberg). Not wrong, but not what a reader wants.
* The audit raised one soft flag (`MD INTERIØRPROSJEKT`): the snippet has line breaks where the value has spaces; the
  verifier compares whitespace-normalised text. Benign.

**Latency is the real cost.** The free tier took 40-65 s per call on this day (the earlier proxy-corpus benchmark saw ~14 s),
so the old 40 s timeout failed every call. The timeout is now `LLM_TIMEOUT_SECONDS` (default 90). At 8 workers, about 11%
of an official batch listing a website, a 1,000-company batch would spend roughly 10 minutes in LLM calls; the wall-clock
deadline and request budget still apply, and a failed or slow call just leaves description/services out.
The injection risk measured in `BENCHMARK.md` is unchanged: the verifier stops text that is not on the page, not text that
is on the page and hostile.

## Website discovery for companies with no registered website (2026-10-04)
~89% of companies list no website, so they got no web facts at all. New: domain names built from the legal name
(`nordvikbygg.no`, `nordvik-bygg.no`, `nordvik.no` for a distinctive first word, `nordvikbygg.com`; at most 4) are tried as
**candidates only** (RULES.md: discovery generates candidates, not evidence). A candidate is probed with robots + homepage,
dropped unless its homepage mentions a distinctive word of the company's name (or its organisation number), and then
run through the normal identity gate with a **stricter threshold, 0.95**: the organisation number, or the full legal name
plus the exact street address. A guessed domain that forwards to a different name (a directory, a parent) is never accepted.
Housing co-ops, foundations, funds and names made only of generic words get no candidates. Switch off with
`--no-discovery` or `DISCOVER_WEBSITES=0`. Files: `reports/discovery-200/`, sample `samples/nowebsite200.jsonl`.

On 200 randomly drawn companies without a registered website (174 had a name that allows candidates):
| | |
|---|---|
| websites found and verified | **12 (6.0%)**; 11 by organisation number or name + address in the snippet, 1 by name + street |
| candidates tried that do not exist | ~400 of ~430 (a dead host costs one request) |
| candidates refused | a few: another company, forwards elsewhere, name absent, robots.txt |
| extra requests | about 3 per company without a website (run total 1,290 = 6.45/company with per-company register calls) |
| facts on those 12 | description 7, email 12, phone 10, Facebook 3, dated activity 3, careers page 1 |
| automated audit | 0 hard / 0 soft flags |

A first run found one defect before this was recorded: a guessed domain that forwarded to a **directory page** about the
company was accepted as its website (`vvseksperten.no/...`). Cross-domain forwarding is now rejected unless it is the
same name with other hyphens/suffix (`ltsflyfishing.com` to `lts-flyfishing.com`, which carried the organisation number). All 12
accepted sites were read against their identity snippet by hand; I found no wrong company, but 12 is a small number.

What this means: in an official batch where ~89% of companies list no site, discovery roughly adds 5 percentage points of
companies with web facts on top of the ~3.5% covered through registered sites (my estimate from this one sample).
**Budget:** at ~3 requests per undiscovered-site company, a 1,500-company batch would need ~6,000 requests for discovery. The
planner puts discovery after the cheaper tiers, so under the default 2,000-request limit only part of the batch is tried; if
Builderr's real request limit is higher, raise `REQUEST_BUDGET_TOTAL`.
