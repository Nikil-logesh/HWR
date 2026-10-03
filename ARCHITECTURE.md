# Architecture

Authority order: RULES.md > kit/ > task prompt. `kit/` is untouched; `src/signalpost` imports
`kit/src/norway_company_agent` as a library and adds the pieces below.

## Pipeline per company (one terminal envelope each, never dropped)
1. **Register layer (no LLM):** bulk CSV row (free, one download) + live Brreg endpoints
   (accounts, roles, subunits, group) subject to a per-company request budget.
   Identity anchor = organisation number. Financial values come only from the official accounts API.
2. **Website layer:** registry website field only; no website = fast path (0 requests).
   Identity score from org number / legal name / address; below threshold => register-only facts.
3. **LLM text extraction (optional):** only on identity-verified, already-fetched pages; a code verifier
   requires each `claim_span` to literally contain the value, else the fact is dropped.
4. **Refresh:** previous profiles in SQLite; diff -> `changes[]`; unchanged facts get refreshed check dates.
5. **Envelope:** kit `OUTPUT_CONTRACT.md` shape; availability states
   available / not_available / blocked / not_applicable / ambiguous / failed.

## Controls
Global request budget, per-company budget, concurrency cap, wall-clock cutoff that writes a
`failed`/budget envelope for every unprocessed company (exactly one envelope per input).

## Known environment limit
The build sandbox blocks data.brreg.no, builderr.ai and LLM hosts; live behaviour is tested via fixtures only.
