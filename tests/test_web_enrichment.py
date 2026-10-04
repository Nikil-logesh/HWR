"""Phase 4 gate: identity matching, literal-snippet verification, fail-closed and no-website fast path.
HTML pages are synthetic; network is replaced by httpx.MockTransport."""
import json
import time

import httpx

from signalpost.budget import Budget
from signalpost.claims import ClaimSet
from signalpost.web.enrich import enrich_website
from signalpost.web.fetch import WebFetcher
from signalpost.web.identity import CompanyIdentity, assess
from signalpost.web.llm import LlmClient, Provider
from signalpost.web.safe import UnsafeUrl, check_public_url
from signalpost.web.text import parse_page
from signalpost.web.verify import Candidate, verify

ORG = "910000012"  # synthetic, valid mod-11
OUR = CompanyIdentity(ORG, "NORDVIK BYGG AS", street="Havnegata 12", postcode="6003", city="ÅLESUND",
                      municipality="ÅLESUND", phone="+47 70 12 34 56")

GOOD = """<html><head><title>Nordvik Bygg</title>
<meta name="description" content="Nordvik Bygg bygger og rehabiliterer boliger og næringsbygg på Sunnmøre."></head>
<body><h1>Nordvik Bygg AS</h1><p>Vi utfører totalentreprise og rehabilitering av eldre bygg.</p>
<a href="/kontakt">Kontakt</a><a href="https://www.facebook.com/nordvikbygg">Facebook</a>
<footer>Nordvik Bygg AS, Havnegata 12, 6003 Ålesund. Org.nr. 910 000 012. Epost: post@nordvikbygg.example
Telefon: 70 12 34 56</footer></body></html>"""
CONTACT = "<html><body><h1>Kontakt oss</h1><p>Ring oss på 70 12 34 56 eller post@nordvikbygg.example</p></body></html>"
# Similarly named DIFFERENT company: same name core, other town, different org number
LOOKALIKE = """<html><head><title>Nordvik Bygg</title></head><body><h1>Nordvik Bygg AS</h1>
<p>Entreprenør i Bergen. Storgata 5, 5003 Bergen. Org.nr 910 000 020. Telefon 55 11 22 33</p></body></html>"""
NAME_ONLY = "<html><head><title>Nordvik Bygg</title></head><body><h1>Nordvik Bygg</h1><p>Vi bygger hus.</p></body></html>"
PUBLIC = lambda host, port, **kw: [(2, 1, 6, "", ("93.184.216.34", 0))]


def site(pages, robots="User-agent: *\nAllow: /"):
    hits = []

    def handler(req: httpx.Request):
        hits.append(str(req.url))
        if req.url.path == "/robots.txt":
            return httpx.Response(200, text=robots) if robots is not None else httpx.Response(404)
        body = pages.get(req.url.path)
        return httpx.Response(200, text=body, headers={"content-type": "text/html; charset=utf-8"}) if body \
            else httpx.Response(404)
    return httpx.MockTransport(handler), hits


def run(pages, llm=None, ident=OUR, website="nordvik.example", **kw):
    transport, hits = site(pages, **kw)
    budget = Budget(100, 15)
    f = WebFetcher(budget, transport=transport, resolver=PUBLIC, sleeper=lambda s: None)
    cs = ClaimSet()
    out = enrich_website(cs, ident, website, f, llm)
    return cs, out, hits


def claims(cs):
    return {c.field: c for c in cs.claims}


# ---------- (a) similarly named different company is rejected ----------
def test_lookalike_company_is_rejected_fail_closed():
    cs, out, _ = run({"/": LOOKALIKE})
    c = claims(cs)
    assert out.state == "ambiguous" and c["official_website"].availability == "ambiguous"
    assert "different organisation number (910000020)" in c["official_website"].note
    assert set(c) == {"official_website"}  # no web fact published for the wrong company


def test_name_only_match_is_not_enough():
    cs, out, _ = run({"/": NAME_ONLY})
    assert out.state == "ambiguous" and out.identity.score == 0.5 and set(claims(cs)) == {"official_website"}


def test_name_plus_municipality_only_is_not_publishable():
    res = assess(OUR, [parse_page("https://x.example/", "<html><body>Nordvik Bygg AS holder til i Ålesund</body></html>")])
    assert res.score == 0.70 and not res.publishable


def test_correct_company_verified_by_org_number_and_publishes_facts():
    cs, out, _ = run({"/": GOOD, "/kontakt": CONTACT})
    c = claims(cs)
    assert out.state == "verified" and out.identity.score == 1.0 and "organisation_number" in out.identity.signals
    assert c["official_website"].availability == "available" and c["official_website"].confidence == 1.0
    assert c["website_description"].value.startswith("Nordvik Bygg bygger")
    assert c["contact_email_1"].value == "post@nordvikbygg.example"
    assert c["contact_phone_1"].value == "70 12 34 56"
    assert c["social_facebook"].value == "https://www.facebook.com/nordvikbygg"
    for cl in (c for c in cs.claims if c.availability == "available"):
        ev = next(e for e in cs.evidence if e.id == cl.evidence_ids[0])
        assert ev.source_class == "company_owned_website" and ev.claim_span and ev.content_sha256


def test_name_plus_street_address_verifies_without_org_number():
    html = GOOD.replace("Org.nr. 910 000 012.", "")
    res = assess(OUR, [parse_page("https://x.example/", html)])
    assert res.score == 0.95 and res.signals == ["legal_name", "street_address"] and res.publishable


def test_foreign_org_number_vetoes_even_if_name_and_address_match():
    html = GOOD.replace("910 000 012", "910 000 020")
    res = assess(OUR, [parse_page("https://x.example/", html)])
    assert res.veto and not res.publishable


def test_parked_domain_rejected():
    res = assess(OUR, [parse_page("https://x.example/", "<html><body>Nordvik Bygg AS - this domain is for sale</body></html>")])
    assert not res.publishable and res.veto


# ---------- (b) fabricated value without snippet support is dropped ----------
def test_verifier_rules():
    corpus = {"u": "Vi bygger boliger i Ålesund.\nTelefon 70 12 34 56"}
    ok = Candidate("products_services", "bygger boliger", "Vi bygger boliger i Ålesund.", "u", "llm")
    assert verify(ok, corpus) == (True, "ok")
    assert not verify(Candidate("f", "bygger broer", "Vi bygger boliger i Ålesund.", "u", "llm"), corpus)[0]
    assert not verify(Candidate("f", "bygger broer", "Vi bygger broer", "u", "llm"), corpus)[0]  # snippet invented
    assert not verify(Candidate("f", "x", "Vi bygger boliger i Ålesund.", "other", "llm"), corpus)[0]
    assert not verify(Candidate("f", "", "", "u", "llm"), corpus)[0]


def llm_returning(payload):
    def handler(req):
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(payload)}}],
                                         "usage": {"prompt_tokens": 100, "completion_tokens": 20}})
    budget = Budget(100, 15)
    return LlmClient([Provider("primary", "https://llm.example/v1", "m", "k")], budget,
                     transport=httpx.MockTransport(handler), sleeper=lambda s: None)


def test_fabricated_llm_facts_are_dropped_and_real_ones_kept():
    payload = {"description": None, "services": [
        {"page": 1, "value": "totalentreprise", "evidence_snippet": "Vi utfører totalentreprise og rehabilitering av eldre bygg."},
        {"page": 1, "value": "gratis solcellepaneler", "evidence_snippet": "Vi installerer gratis solcellepaneler"},
        {"page": 1, "value": "omsetning 500 MNOK", "evidence_snippet": "Vi utfører totalentreprise"}]}
    html = GOOD.replace('<meta name="description"', '<meta name="x"')
    cs, out, _ = run({"/": html}, llm=llm_returning(payload))
    assert claims(cs)["products_services"].value == ["totalentreprise"]
    reasons = {d["value"]: d["reason"] for d in out.dropped}
    assert reasons["gratis solcellepaneler"] == "snippet not found in page"
    assert reasons["omsetning 500 MNOK"] == "snippet does not contain value"
    assert not any(k.startswith("financials") for k in claims(cs))


def test_llm_not_called_when_identity_fails():
    llm = llm_returning({"description": None, "services": []})
    _, out, _ = run({"/": LOOKALIKE}, llm=llm)
    assert llm.usage.requests == 0 and out.published == 0


# ---------- (c) low identity => register-only output ----------
def test_low_identity_publishes_nothing_but_the_ambiguous_state():
    cs, _, _ = run({"/": NAME_ONLY.replace("Vi bygger hus.", "Ring 99 88 77 66 post@x.example")})
    assert [c.field for c in cs.claims] == ["official_website"] and cs.claims[0].availability == "ambiguous"
    assert cs.claims[0].value is None


# ---------- (d) no website is handled fast ----------
def test_no_website_zero_requests_and_fast():
    transport, hits = site({})
    f = WebFetcher(Budget(100, 15), transport=transport, resolver=PUBLIC)
    t = time.monotonic()
    for website in ("", None, "   ", "not a url"):
        cs = ClaimSet()
        out = enrich_website(cs, OUR, website, f)
        assert out.state == "no_website" and out.requests == 0
        assert cs.claims[0].availability == "not_available"
    assert hits == [] and time.monotonic() - t < 0.5


# ---------- robustness: robots, budget, SSRF, redirects ----------
def test_robots_disallow_blocks_fetch():
    cs, out, hits = run({"/": GOOD}, robots="User-agent: *\nDisallow: /")
    assert out.state == "blocked" and claims(cs)["official_website"].availability == "blocked"
    assert all("robots.txt" in h for h in hits)


def test_request_budget_per_company_is_enforced():
    transport, hits = site({"/": GOOD, "/kontakt": CONTACT})
    f = WebFetcher(Budget(100, 2), transport=transport, resolver=PUBLIC, sleeper=lambda s: None)
    cs = ClaimSet()
    out = enrich_website(cs, OUR, "nordvik.example", f)
    assert len(hits) == 2 and out.state == "verified" and "contact_email_1" in claims(cs)  # secondary pages skipped
    transport1, hits1 = site({"/": GOOD})
    f1 = WebFetcher(Budget(100, 1), transport=transport1, resolver=PUBLIC, sleeper=lambda s: None)
    cs1 = ClaimSet()
    out1 = enrich_website(cs1, OUR, "nordvik.example", f1)
    assert len(hits1) == 1 and claims(cs1)["official_website"].availability == "failed" and out1.state == "failed"


def test_typical_company_costs_at_most_four_requests():
    _, out, hits = run({"/": GOOD, "/kontakt": CONTACT, "/om-oss": GOOD})
    assert out.requests == len(hits) <= 4


def test_ssrf_guard():
    for bad in ("http://127.0.0.1/", "http://localhost/x", "http://10.0.0.5/", "http://169.254.169.254/latest",
                "file:///etc/passwd", "ftp://x.example/", "http://user:pw@x.example/", "http://[::1]/"):
        try:
            check_public_url(bad, PUBLIC)
        except UnsafeUrl:
            continue
        raise AssertionError(bad)
    private = lambda host, port, **kw: [(2, 1, 6, "", ("10.1.2.3", 0))]
    try:
        check_public_url("http://intranet.example/", private)
        raise AssertionError("private resolution allowed")
    except UnsafeUrl:
        pass


def test_redirect_to_private_address_is_refused():
    def handler(req):
        if req.url.path == "/robots.txt":
            return httpx.Response(404)
        return httpx.Response(302, headers={"location": "http://169.254.169.254/latest/meta-data"})
    f = WebFetcher(Budget(100, 15), transport=httpx.MockTransport(handler), resolver=PUBLIC, sleeper=lambda s: None)
    cs = ClaimSet()
    out = enrich_website(cs, OUR, "nordvik.example", f)
    assert claims(cs)["official_website"].availability == "blocked" and out.state == "blocked"


def test_dead_site_404_is_not_available_and_timeouts_are_failed():
    cs, _, _ = run({})
    assert claims(cs)["official_website"].availability == "not_available"

    def boom(req):
        if req.url.path == "/robots.txt":
            return httpx.Response(404)
        raise httpx.ConnectTimeout("t")
    f = WebFetcher(Budget(100, 15), transport=httpx.MockTransport(boom), resolver=PUBLIC, sleeper=lambda s: None)
    cs2 = ClaimSet()
    enrich_website(cs2, OUR, "nordvik.example", f)
    assert claims(cs2)["official_website"].availability == "failed"


def test_per_domain_throttle_spaces_requests():
    sleeps, now = [], [0.0]

    def sleep(s):
        sleeps.append(s)
        now[0] += s
    transport, _ = site({"/": GOOD, "/kontakt": CONTACT})
    f = WebFetcher(Budget(100, 15), transport=transport, resolver=PUBLIC, min_interval=1.0,
                   clock=lambda: now[0], sleeper=sleep)
    enrich_website(ClaimSet(), OUR, "nordvik.example", f)
    assert len(sleeps) >= 2 and all(abs(s - 1.0) < 1e-9 for s in sleeps)  # every request waits one interval


def test_llm_provider_fallback_on_429_and_usage_tracking():
    calls = []

    def handler(req):
        calls.append(str(req.url))
        if "primary" in str(req.url):
            return httpx.Response(429, headers={"retry-after": "0"})
        return httpx.Response(200, json={"choices": [{"message": {"content": '{"description": null, "services": []}'}}],
                                         "usage": {"prompt_tokens": 50, "completion_tokens": 5}})
    llm = LlmClient([Provider("primary", "https://primary.example/v1", "a", "k"),
                     Provider("fallback", "https://fallback.example/v1", "b", "k", 0.1, 0.4)],
                    Budget(100, 15), transport=httpx.MockTransport(handler), sleeper=lambda s: None)
    assert llm.complete_json("x", ORG) == {"description": None, "services": []}
    assert llm.usage.by_provider == {"primary": 2, "fallback": 1} and llm.usage.prompt_tokens == 50
    assert abs(llm.usage.cost_usd - (50 * 0.1 + 5 * 0.4) / 1e6) < 1e-12 and len(calls) == 3
    assert LlmClient([], Budget(1, 1)).complete_json("x", ORG) is None


def test_registered_domain_never_collapses_unknown_suffixes():
    from signalpost.web.fetch import registered_domain
    assert registered_domain("https://www.firma.no/x") == "firma.no"
    assert registered_domain("https://shop.firma.co.uk/") == "firma.co.uk"
    assert registered_domain("https://a.firma.example/") == "firma.example"
    assert registered_domain("https://a.example/") != registered_domain("https://b.example/")
    assert registered_domain("not a url") == ""


def test_hostname_fallback_toggles_www_when_the_registered_host_does_not_connect():
    def handler(req):
        if req.url.host == "www.nordvik.example":
            raise httpx.ConnectError("no route")
        if req.url.path == "/robots.txt":
            return httpx.Response(404)
        return httpx.Response(200, text=GOOD, headers={"content-type": "text/html"})
    hits = []

    def spy(req):
        hits.append(req.url.host)
        return handler(req)
    f = WebFetcher(Budget(100, 15), transport=httpx.MockTransport(spy), resolver=PUBLIC, sleeper=lambda s: None)
    cs = ClaimSet()
    out = enrich_website(cs, OUR, "www.nordvik.example", f, None)
    c = {x.field: x for x in cs.claims}
    assert out.state == "verified" and c["official_website"].value.startswith("https://nordvik.example")
    assert hits[:2] == ["www.nordvik.example", "www.nordvik.example"] or "nordvik.example" in hits
    # and the other direction, plus a host where neither form connects
    def dead(req):
        raise httpx.ConnectError("dns")
    f2 = WebFetcher(Budget(100, 15), transport=httpx.MockTransport(dead), resolver=PUBLIC, sleeper=lambda s: None)
    cs2 = ClaimSet()
    out2 = enrich_website(cs2, OUR, "nordvik.example", f2, None)
    assert out2.state == "failed" and out2.requests <= 6
    assert {x.field: x for x in cs2.claims}["official_website"].availability == "failed"
