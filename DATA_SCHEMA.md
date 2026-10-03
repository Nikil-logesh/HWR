# Data schema (envelope)

One JSON object per line, deterministic (sorted keys, compact). Based on `kit/OUTPUT_CONTRACT.md`.
Additions (all optional, additive): top-level `schema_version` and `explanation`; claim `reporting_period`,
`as_of`, `note`; evidence `extraction_method`.

Rules enforced by the Pydantic models: an `available` claim must have a non-null value AND at least one
evidence id; every evidence id must exist; unavailable claims never carry values. Missing is omitted or
`not_available` — never zero. A literal 0 in a source is preserved.

Claim fields (register layer): legal_name, legal_form, status (active/bankrupt/liquidating/forced_dissolution/
deleted), nace, nace_2/3, registered_address, postal_address, employees, founded, registered_at,
latest_accounts_year, vat_registered, institutional_sector, registered_purpose, registered_activity,
registry_website, roles, workplaces, financials.{revenue,operating_result,profit_before_tax,annual_result,
total_assets,equity,total_debt} (+ financials_consolidated.*), financial_history_years, registry_record.
Financial values come only from Regnskapsregisteret JSON numbers and carry reporting_period.

Hiring / activity (company's own verified site only): `careers_page` {url, kind: company_page|external_portal, portal?},
`open_positions` [{title, url?, date?, date_text?, deadline?}], `hiring_status` (`hiring` | `no_open_positions`),
`public_activity` [{title, url?, date, date_text}] (newest first, max 10), `latest_activity_date`. List claims carry one
evidence record per item. States: `not_available` (checked, nothing recognised / none linked), `blocked` (robots.txt),
`failed` (fetch error), `ambiguous` (site names other organisation numbers).

Fixtures: tests/fixtures/recorded = 12 REAL Brreg responses (2026-10-03, birth dates scrubbed); tests/fixtures/synthetic = invented edge cases (bankrupt, liquidating, 410) the active-only pool cannot supply.
