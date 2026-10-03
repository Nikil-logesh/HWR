# Identity resolution and publication gates

The official register record for the organisation number is the identity anchor. A website is only a
candidate until a page proves it belongs to that exact entity. The score is computed in code (`web/identity.py`).

| Score | Evidence on fetched pages | Publishable |
|---|---|---|
| 1.00 | exact organisation number (mod-11 valid, any spacing) | yes |
| 0.95 | full legal name + exact street address | yes |
| 0.92 | full legal name + postcode and city together, or the registered phone number | yes |
| 0.70 | legal name + municipality only | no |
| 0.50 | legal name only | no |

Vetoes: the page gives a *different* valid organisation number as the company's own; parked / for-sale domain.
Threshold 0.90. Below it: `official_website` is `ambiguous`, and NO web fact is published (register-only output).

Web facts (description, services, email, phone, social links) are published only after the literal-snippet
verifier: the snippet must occur in the fetched page and must contain the value (`web/verify.py`).
The LLM may only propose verbatim spans for description/services; it never sees financials and never decides identity.
Social profiles are published only when linked from an identity-verified page AND the handle contains the legal name.
No website in the register => `not_available`, zero requests, no search-based discovery.

Per company the web layer costs at most 4 requests (robots.txt, homepage, 2 secondary pages) plus LLM calls.
Safety: public http(s) only, private/loopback/link-local blocked incl. after redirects, robots.txt honoured,
1 s per-domain throttle, 1 MB body cap. Residual risk: DNS rebinding between check and connect.
