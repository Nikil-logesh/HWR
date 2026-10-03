# Audit: wrong-company checks

A material wrong-company publication blocks an official run, so every profile batch is audited twice.

## Automated (`signalpost.audit`, `make audit`) — runs on the WHOLE file
Hard flags (profile must not be published): `web_facts_without_verified_identity`, `low_identity_confidence`
(official website published below the 0.90 identity threshold), `web_source_domain_mismatch` (a web fact whose
evidence comes from another registered domain than the verified site), `register_evidence_for_other_org`
(a register source URL naming a different organisation number), `legal_name_differs_from_universe`,
`financial_not_from_official_api`. Soft flags: `foreign_org_number_in_web_snippet`,
`website_claims_without_snippet_support`. Exit code 1 on any hard flag.

## Human (`scripts/audit_sample.py`) — 50 seeded random profiles
Writes `out/audit/audit_sheet.md` (per company: register link, every REGISTER and WEB fact with source URL, snippet and
confidence) and `audit_sheet.csv` (with a verdict column: ok / wrong company / wrong value / unsupported).
Up to half of the sample is drawn from profiles that carry web facts, because those are where a wrong-company error can
occur; the register layer is keyed by the organisation number itself.

Reviewer procedure: open the register link and compare identity rows; for each WEB row open the source URL and confirm
(1) the page is this company (organisation number, or name + address), (2) the snippet is on the page and contains the
value. One "wrong company" verdict means the identity gate has a hole: tighten `web/identity.py` and re-run.
