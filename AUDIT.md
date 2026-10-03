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

## First batch (2026-10-03, 1,500 seeded companies, register layer only)
`make batch` -> 1,500 of 1,500 envelopes, 1,494 completed + 6 partial, 1,834 requests (1.22 per company), 288 s, $0,
contract validation passed. Audit: 0 hard flags, 3 soft flags. All 3 are renames: the current Brreg bulk CSV holds
a different name than the (older) frozen universe row for the same organisation number, e.g. 917265984 now
`LG RENTAL AS` (was `LIER MASKINUTLEIE AS`). That check was first written as a hard flag; it was downgraded after
inspection because the entity record's own organisation number was verified. Note the consequence: the frozen universe
file is not current, so names must come from the register, never from the universe row, when both are available.
The 6 partial profiles are accounts-endpoint HTTP 500 answers (a bank, a pension fund, a securities fund, 2 foundations,
1 ordinary AS), recorded as `failed` for accounts while all other facts are published.
Limitation: this sandbox cannot reach company websites, so the batch contains NO web facts and the web half of the
audit sheet is empty. The web layer's wrong-company protection is covered by tests, not by a live audit; a batch
run where websites are reachable must be audited before anything is trusted.
