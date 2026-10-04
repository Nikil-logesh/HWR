"""Website discovery for companies without a registered website: candidates only, proven by the identity gate with a
stricter threshold. HTML is synthetic; the network is httpx.MockTransport (unknown hosts fail like a missing domain)."""
import httpx

from signalpost.budget import Budget
from signalpost.claims import ClaimSet
from signalpost.planner import Company, plan_batch
from signalpost.web.discover import candidate_urls, plausibly_the_company, worth_trying
from signalpost.web.enrich import discover_website
from signalpost.web.fetch import WebFetcher
from signalpost.web.identity import CompanyIdentity

ORG = "910000012"
OUR = CompanyIdentity(ORG, "NORDVIK BYGG AS", street="Havnegata 12", postcode="6003", city="ÅLESUND", municipality="ÅLESUND")
PUBLIC = lambda host, port, **kw: [(2, 1, 6, "", ("93.184.216.34", 0))]

OURS = ("<html><head><meta name='description' content='Nordvik Bygg bygger boliger og næringsbygg på Sunnmøre i mange år.'>"
        "</head><body><h1>Nordvik Bygg AS</h1><p>Havnegata 12, 6003 Ålesund. Org.nr. 910 000 012. post@nordvikbygg.no</p></body></html>")
OTHER = "<html><body><h1>Nordvik Bygg</h1><p>Entreprenør i Bergen. Storgata 5, 5003 Bergen. Org.nr 910 000 020.</p></body></html>"
NAME_ONLY = "<html><body><h1>Nordvik Bygg AS</h1><p>Vi bygger hus på Sunnmøre. Ring oss.</p></body></html>"
WEAK = "<html><body><h1>Nordvik Bygg AS</h1><p>Besøk oss i 6003 Ålesund. Vi bygger hus.</p></body></html>"  # 0.92: not enough


def world(sites):
    """sites: {host: html}; hosts not listed do not exist (connection error)."""
    hits = []

    def handler(req: httpx.Request):
        hits.append(str(req.url))
        host = req.url.host
        if host not in sites:
            raise httpx.ConnectError("no such host", request=req)
        if req.url.path == "/robots.txt":
            return httpx.Response(404)
        return httpx.Response(200, text=sites[host], headers={"content-type": "text/html; charset=utf-8"})
    return httpx.MockTransport(handler), hits


def run(sites, ident=OUR, hint=None):
    transport, hits = world(sites)
    f = WebFetcher(Budget(200, 30), transport=transport, resolver=PUBLIC, sleeper=lambda s: None)
    cs = ClaimSet()
    out = discover_website(cs, ident, f, None, hint=hint)
    return cs, out, hits


def site_claim(cs):
    return next(c for c in cs.claims if c.field == "official_website")


def test_candidates_are_built_from_the_legal_name_only():
    assert candidate_urls("NORDVIK BYGG AS") == ["https://nordvikbygg.no/", "https://nordvik-bygg.no/", "https://nordvikbygg.com/"]
    assert candidate_urls("ÅSE & SØNN AS")[0] == "https://asesonn.no/"  # ASCII-folded
    assert candidate_urls("ARLEAL AS") == ["https://arleal.no/", "https://arleal.com/"]


def test_names_that_cannot_identify_a_domain_get_no_candidates():
    assert not worth_trying("BORETTSLAGET SOLBAKKEN") and not worth_trying("SAMEIET TOU PARK V")
    assert not worth_trying("HOLDING AS") and not worth_trying("AB AS")
    assert candidate_urls("STIFTELSEN KONGSBERG JAZZFESTIVAL") == []


def test_a_candidate_that_proves_identity_is_published_and_says_how_it_was_found():
    cs, out, hits = run({"nordvikbygg.no": OURS})
    c = site_claim(cs)
    assert out.state == "verified" and c.availability == "available" and c.value == "https://nordvikbygg.no/"
    assert c.confidence >= 0.95 and "not listed in the register" in c.note
    ev = next(e for e in cs.evidence if e.id == c.evidence_ids[0])
    assert ev.extraction_method.startswith("domain_candidate+identity_gate:")
    assert not any("nordvik-bygg" in h or ".com" in h for h in hits)  # stops at the first proven candidate


def test_a_different_company_on_a_guessed_domain_is_not_published():
    cs, _, _ = run({"nordvikbygg.no": OTHER})
    c = site_claim(cs)
    assert c.availability == "ambiguous" and "different organisation number (910000020)" in c.note
    assert not any(x.field != "official_website" for x in cs.claims)


def test_name_only_or_weak_evidence_is_below_the_discovery_threshold():
    for page in (NAME_ONLY, WEAK):
        cs, _, _ = run({"nordvikbygg.no": page})
        c = site_claim(cs)
        assert c.availability == "ambiguous" and c.value is None, page
        assert "candidate domain built from the legal name" in c.note
        assert not any(x.field == "contact_phone_1" or x.field == "website_description" for x in cs.claims)


def test_a_candidate_that_never_mentions_the_company_costs_no_extra_pages():
    cs, _, hits = run({"nordvikbygg.no": "<html><body>Velkommen til en helt annen butikk.</body></html>"})
    c = site_claim(cs)
    assert c.availability == "not_available" and "does not mention the company" in c.note
    assert len([h for h in hits if "nordvikbygg.no" in h]) == 2  # robots + homepage, nothing more


def test_nonexistent_domains_cost_one_request_each_and_end_as_not_available():
    cs, out, hits = run({})
    c = site_claim(cs)
    assert c.availability == "not_available" and out.requests == 3 and len(hits) == 3
    assert "unreachable" in c.note


def test_a_site_found_on_an_earlier_run_is_rechecked_directly_not_guessed_again():
    _, out, hits = run({"nordvik.example": OURS}, hint="https://nordvik.example/")
    assert out.state == "verified" and all("nordvik.example" in h for h in hits)


def test_planner_spends_on_discovery_only_after_the_cheaper_tiers_and_only_for_discoverable_companies():
    cos = [Company("1", discoverable=True), Company("2"), Company("3", True)]
    plans = plan_batch(cos, 1000, 15)
    assert plans["1"].discover and not plans["2"].discover and plans["3"].web and not plans["3"].discover
    tight = plan_batch([Company(str(i), discoverable=True) for i in range(50)], 100, 15)  # 2 per company
    assert not any(p.discover for p in tight.values()) and all("financials" in p.modules for p in tight.values())


def test_plausibility_prefilter_uses_distinctive_words_or_the_org_number():
    assert plausibly_the_company(OUR, "velkommen til nordvik bygg") and not plausibly_the_company(OUR, "bygg og anlegg")
    assert plausibly_the_company(OUR, "org nr 910000012")
