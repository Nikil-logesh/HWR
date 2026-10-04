"""Hiring + dated-activity extraction: synthetic company sites only (the sandbox cannot reach real websites)."""
import datetime as dt
import json

import httpx

from signalpost import htmlreport
from signalpost.budget import Budget
from signalpost.claims import ClaimSet
from signalpost.explain import explain
from signalpost.httpcache import ApiClient
from signalpost.models import Envelope
from signalpost.pipeline import register_envelope
from signalpost.store import SnapshotStore
from signalpost.validate import validate_envelope
from signalpost.web import signals as sg
from signalpost.web.enrich import enrich_website
from signalpost.web.fetch import WebFetcher
from signalpost.web.identity import CompanyIdentity
from test_register_layer import load, transport_for

TODAY = dt.date(2026, 10, 3)
OUR = CompanyIdentity("910000012", "NORDVIK BYGG AS", street="Havnegata 12", postcode="6003", city="ÅLESUND",
                      municipality="ÅLESUND", phone="+47 70 12 34 56")
PUBLIC = lambda host, port, **kw: [(2, 1, 6, "", ("93.184.216.34", 0))]

HOME = """<html><head><title>Nordvik Bygg</title>
<meta name="description" content="Nordvik Bygg bygger og rehabiliterer boliger og næringsbygg på Sunnmøre.">
<link rel="alternate" type="application/rss+xml" href="/feed.xml">%(head)s</head>
<body><h1>Nordvik Bygg AS</h1><nav><a href="/karriere">Karriere</a> <a href="/nyheter">Nyheter</a></nav>
<footer>Nordvik Bygg AS, Havnegata 12, 6003 Ålesund. Org.nr. 910 000 012. Telefon 70 12 34 56</footer>%(body)s</body></html>"""


def home(head="", body="", feed=True, careers=True, news=True):
    html = HOME % {"head": head, "body": body}
    if not feed:
        html = html.replace('<link rel="alternate" type="application/rss+xml" href="/feed.xml">', "")
    if not careers:
        html = html.replace('<a href="/karriere">Karriere</a>', "")
    if not news:
        html = html.replace('<a href="/nyheter">Nyheter</a>', "")
    return html


def site(pages, robots="User-agent: *\nAllow: /"):
    hits = []

    def handler(req: httpx.Request):
        hits.append(req.url.path)
        if req.url.path == "/robots.txt":
            return httpx.Response(200, text=robots)
        page = pages.get(req.url.path)
        if page is None:
            return httpx.Response(404)
        body, ctype = page if isinstance(page, tuple) else (page, "text/html; charset=utf-8")
        return httpx.Response(200, text=body, headers={"content-type": ctype})
    return httpx.MockTransport(handler), hits


def run(pages, ident=OUR, robots="User-agent: *\nAllow: /", cap=15, **kw):
    transport, hits = site(pages, robots)
    f = WebFetcher(Budget(500, cap), transport=transport, resolver=PUBLIC, sleeper=lambda s: None)
    cs = ClaimSet()
    out = enrich_website(cs, ident, "nordvik.example", f, None, today=TODAY, **kw)
    return cs, out, hits, {c.field: c for c in cs.claims}


def evidence_of(cs, claim):
    by = {e.id: e for e in cs.evidence}
    return [by[i] for i in claim.evidence_ids]


RSS = """<?xml version="1.0"?><rss version="2.0"><channel><title>Nordvik</title>
<item><title>Nytt bygg ferdigstilt i Ålesund</title><link>https://nordvik.example/nyheter/1</link><pubDate>Mon, 14 Sep 2026 09:00:00 +0200</pubDate></item>
<item><title>Vi har fått ny daglig leder</title><link>/nyheter/2</link><pubDate>Fri, 03 Jul 2026 08:00:00 +0200</pubDate></item>
<item><title>Undated post that must be ignored</title><link>/nyheter/3</link></item>
<item><title>Future dated post</title><link>/nyheter/4</link><pubDate>Mon, 14 Sep 2027 09:00:00 +0200</pubDate></item>
</channel></rss>"""
XML = "application/rss+xml"


# ---------- dates ----------
def test_parse_date_formats_and_rejections():
    assert sg.parse_date("Publisert 12.10.2026 kl 10") == ("2026-10-12", "12.10.2026")
    assert sg.parse_date("12. oktober 2026") == ("2026-10-12", "12. oktober 2026")
    assert sg.parse_date("3 okt 2026")[0] == "2026-10-03" and sg.parse_date("Oct 3, 2026")[0] == "2026-10-03"
    assert sg.parse_date("2026-02-28T10:00:00Z")[0] == "2026-02-28" and sg.parse_date("5/1/2026")[0] == "2026-01-05"
    assert sg.parse_date("31.02.2026") is None and sg.parse_date("no date here") is None
    assert sg.parse_date("1.5.1999") is None  # not 20xx
    assert sg.plausible_past("2026-10-03", TODAY) and not sg.plausible_past("2026-10-05", TODAY)
    assert not sg.plausible_past("1999-12-31", TODAY)


def test_discover_links_prefers_shallow_same_site_and_recognises_portals():
    anchors = [("https://nordvik.example/om-oss/karriere/trainee", "Trainee"), ("https://nordvik.example/karriere", "Karriere"),
               ("https://evil.example/karriere", "Karriere"), ("https://nordvik.teamtailor.com/jobs", "Ledige stillinger"),
               ("https://nordvik.example/nyheter", "Nyheter"), ("https://nordvik.example/", "Hjem")]
    s = sg.discover_links("https://nordvik.example/", anchors, ["https://nordvik.example/feed.xml", "https://x.example/f"])
    assert s.careers_urls[0] == "https://nordvik.example/karriere" and "evil.example" not in " ".join(s.careers_urls)
    assert s.portal[0] == "Teamtailor" and s.news_urls == ["https://nordvik.example/nyheter"]
    assert s.feed_urls == ["https://nordvik.example/feed.xml"]


def test_how_we_work_is_not_a_careers_link():  # real: /news/slikjobbervi ("Slik jobber vi" = how we work) was a careers page
    anchors = [("https://nordvik.example/news/slikjobbervi", "Slik jobber vi"), ("https://nordvik.example/jobbe-hos-oss", "Jobbe hos oss?")]
    assert sg.discover_links("https://nordvik.example/", anchors, []).careers_urls == ["https://nordvik.example/jobbe-hos-oss"]


# ---------- hiring ----------
JOBLD = """<script type="application/ld+json">{"@context":"https://schema.org","@type":"JobPosting","title":"Tømrer / Byggfagarbeider",
"datePosted":"2026-09-20","validThrough":"2026-11-01","hiringOrganization":{"@type":"Organization","name":"Nordvik Bygg AS"},
"url":"https://nordvik.example/karriere/tomrer"}</script>"""


def test_jobposting_jsonld_published_with_literal_evidence_and_dates():
    careers = f"<html><body><h1>Karriere</h1>{JOBLD}</body></html>"
    cs, _out, _hits, c = run({"/": home(feed=False, news=False), "/karriere": careers})
    pos = c["open_positions"]
    assert pos.availability == "available" and pos.value[0]["title"] == "Tømrer / Byggfagarbeider"
    assert pos.value[0]["date"] == "2026-09-20" and pos.value[0]["deadline"] == "2026-11-01"
    ev = evidence_of(cs, pos)
    assert len(ev) == 1 and ev[0].source_url.endswith("/karriere") and ev[0].claim_span.startswith('"title"')
    assert c["hiring_status"].value == "hiring" and c["careers_page"].value["kind"] == "company_page"
    assert c["careers_page"].value["url"] == "https://nordvik.example/karriere"
    assert not [e for e in cs.evidence if e.source_class != "company_owned_website" and "karriere" in e.source_url]


def test_jobposting_title_needing_json_escapes_is_dropped_not_distorted():
    quoted = JOBLD.replace("Tømrer / Byggfagarbeider", 'Tømrer / \\"Byggfagarbeider\\"')
    _, out, _, c = run({"/": home(feed=False, news=False), "/karriere": f"<html><body>{quoted}</body></html>"})
    assert c["open_positions"].availability == "not_available"
    assert any(d["reason"] == "snippet does not contain value" for d in out.dropped)  # literal check is never relaxed


def test_jobposting_for_another_organisation_is_dropped():
    other = JOBLD.replace("Nordvik Bygg AS", "Rekruttering Partner AS")
    _cs, out, _, c = run({"/": home(feed=False, news=False), "/karriere": f"<html><body>{other}</body></html>"})
    assert c["open_positions"].availability == "not_available" and "hiring_status" not in c
    assert any("hiringOrganization" in d["reason"] for d in out.dropped)
    missing = JOBLD.replace('"hiringOrganization":{"@type":"Organization","name":"Nordvik Bygg AS"},', "")
    _, out2, _, c2 = run({"/": home(feed=False, news=False), "/karriere": f"<html><body>{missing}</body></html>"})
    assert c2["open_positions"].availability == "not_available" and out2.dropped


LISTING = """<html><body><h1>Ledige stillinger</h1><ul>
<li><a href="/karriere/tomrer-2026">Tømrer</a> Søknadsfrist: 15.11.2026 Fast stilling Ålesund</li>
<li><a href="/karriere/prosjektleder">Prosjektleder bygg</a> Publisert 1. oktober 2026 · Heltid</li>
</ul><a href="/karriere/alle">Les mer</a> <a href="/karriere/sok">Søk nå</a> <a href="/karriere/info">Alle stillinger</a>
<a href="/karriere/lonnsomhet-og-mangfold">Om oss som arbeidsgiver</a></body></html>"""


def test_listing_requires_context_and_ignores_navigation():
    cs, _, _, c = run({"/": home(feed=False, news=False), "/karriere": LISTING})
    titles = [i["title"] for i in c["open_positions"].value]
    assert titles == ["Tømrer", "Prosjektleder bygg"]  # nav links and the context-free anchor are not jobs
    assert c["open_positions"].value[0]["deadline"] == "2026-11-15" and "date" not in c["open_positions"].value[0]
    assert c["open_positions"].value[1]["date"] == "2026-10-01"
    assert len(c["open_positions"].evidence_ids) == 2  # one evidence record per item
    assert "Søknadsfrist" in evidence_of(cs, c["open_positions"])[0].claim_span


def test_no_openings_statement_and_unrecognised_careers_page():
    cs, _, _, c = run({"/": home(feed=False, news=False),
                       "/karriere": "<html><body><h1>Karriere</h1><p>For øyeblikket har vi ingen ledige stillinger.</p></body></html>"})
    assert c["hiring_status"].value == "no_open_positions" and c["open_positions"].availability == "not_available"
    assert "no open positions" in c["open_positions"].note and evidence_of(cs, c["hiring_status"])
    _, _, _, en = run({"/": home(feed=False, news=False), "/karriere": "<html><body>There are no open positions right now.</body></html>"})
    assert en["hiring_status"].value == "no_open_positions"
    _, _, _, vague = run({"/": home(feed=False, news=False), "/karriere": "<html><body><h1>Jobb hos oss</h1><p>Vi er et godt miljø.</p></body></html>"})
    assert vague["open_positions"].availability == "not_available" and "no job listings recognised" in vague["open_positions"].note
    assert "hiring_status" not in vague  # unknown is never turned into "not hiring"


def test_external_portal_is_recorded_not_fetched():
    h = home(feed=False, news=False, careers=False, body='<a href="https://nordvik.teamtailor.com/jobs">Ledige stillinger</a>')
    _cs, _, hits, c = run({"/": h})
    assert c["careers_page"].value == {"url": "https://nordvik.teamtailor.com/jobs", "kind": "external_portal", "portal": "Teamtailor"}
    assert c["open_positions"].availability == "not_available" and "Teamtailor" in c["open_positions"].note
    assert hits == ["/robots.txt", "/"]  # the portal host is never contacted


def test_no_careers_link_is_an_honest_not_available_with_no_extra_requests():
    _, _out, hits, c = run({"/": home(feed=False, news=False, careers=False)})
    assert c["open_positions"].availability == "not_available" and "no careers or jobs page" in c["open_positions"].note
    assert "careers_page" not in c and hits == ["/robots.txt", "/"]


# ---------- dated activity ----------
def test_rss_feed_items_are_dated_sorted_and_literal():
    cs, _out, hits, c = run({"/": home(careers=False, news=False), "/feed.xml": (RSS, XML)})
    act = c["public_activity"]
    assert [i["title"] for i in act.value] == ["Nytt bygg ferdigstilt i Ålesund", "Vi har fått ny daglig leder"]
    assert [i["date"] for i in act.value] == ["2026-09-14", "2026-07-03"] and act.as_of == "2026-09-14"
    assert c["latest_activity_date"].value == "2026-09-14"
    ev = evidence_of(cs, act)
    assert all(e.claim_span in RSS for e in ev) and all("<title>" in e.claim_span for e in ev)  # verbatim feed slices
    assert act.value[1]["url"] == "https://nordvik.example/nyheter/2"
    assert "/nyheter" not in hits  # a usable feed makes the news page unnecessary
    assert "Undated post that must be ignored" not in json.dumps(act.value)
    assert "Future dated post" not in json.dumps(act.value)  # undated and future-dated items are never published


def test_feed_with_external_entity_is_not_expanded():
    evil = """<?xml version="1.0"?><!DOCTYPE r [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><rss><channel>
<item><title>Aktuelt &xxe; nytt</title><pubDate>Mon, 14 Sep 2026 09:00:00 +0200</pubDate></item></channel></rss>"""
    cs, _, _, c = run({"/": home(careers=False, news=False), "/feed.xml": (evil, XML)})
    blob = json.dumps([x.model_dump(mode="json") for x in cs.claims] + [e.model_dump(mode="json") for e in cs.evidence])
    assert "root:" not in blob and "/bin/" not in blob  # the file:// entity was never resolved
    assert c["public_activity"].availability in ("available", "not_available")  # parsed safely either way


NEWS = """<html><body><h1>Nyheter</h1>
<article><time datetime="2026-09-30">30. september 2026</time><h2><a href="/nyheter/a">Nordvik vinner rehabiliteringsprosjekt</a></h2></article>
<article><time datetime="2026-08-12">12.08.2026</time><h2>Sommerfest for ansatte</h2></article>
<article><h2>Artikkel uten dato</h2></article>
<article><time datetime="2026-07-01"></time><h2>Dato kun i attributt</h2></article>
</body></html>"""


def test_html_news_items_need_a_visible_real_date():
    cs, _, hits, c = run({"/": home(feed=False, careers=False), "/nyheter": NEWS})
    titles = [i["title"] for i in c["public_activity"].value]
    assert titles == ["Nordvik vinner rehabiliteringsprosjekt", "Sommerfest for ansatte"]
    first = c["public_activity"].value[0]
    assert first["date"] == "2026-09-30" and first["url"] == "https://nordvik.example/nyheter/a"
    assert "30. september 2026" in evidence_of(cs, c["public_activity"])[0].claim_span
    assert hits.count("/nyheter") == 1


def test_news_jsonld_articles():
    ld = """<script type="application/ld+json">{"@type":"NewsArticle","headline":"Ny rapport om byggekostnader","datePublished":"2026-09-01T08:00:00+02:00","url":"https://nordvik.example/n/9"}</script>"""
    _, _, _, c = run({"/": home(feed=False, careers=False), "/nyheter": f"<html><body>{ld}</body></html>"})
    assert c["public_activity"].value[0]["title"] == "Ny rapport om byggekostnader" and c["public_activity"].value[0]["date"] == "2026-09-01"


def test_no_dated_items_is_not_available_and_says_what_was_checked():
    _, _, _, c = run({"/": home(feed=False, careers=False), "/nyheter": "<html><body><h1>Nyheter</h1><p>Kommer snart.</p></body></html>"})
    assert c["public_activity"].availability == "not_available" and "/nyheter" in c["public_activity"].note
    assert "latest_activity_date" not in c
    _, _, _, bare = run({"/": home(feed=False, careers=False, news=False)})
    assert "no news page, feed or dated items found" in bare["public_activity"].note


# ---------- safety, budget, robots, identity ----------
def test_robots_disallow_blocks_only_the_disallowed_section():
    _, _, hits, c = run({"/": home(), "/karriere": LISTING, "/feed.xml": (RSS, XML)},
                        robots="User-agent: *\nDisallow: /karriere")
    assert c["open_positions"].availability == "blocked" and "/karriere" not in hits
    assert c["public_activity"].availability == "available"


def test_extra_pages_are_bounded_by_the_company_request_budget():
    _, _, hits, _ = run({"/": home(), "/karriere": LISTING, "/feed.xml": (RSS, XML), "/nyheter": NEWS})
    assert len(hits) <= 7 and "/nyheter" not in hits  # robots + home + careers + feed (news skipped: feed worked)
    _, _, hits2, c2 = run({"/": home(), "/karriere": LISTING, "/feed.xml": (RSS, XML)}, cap=3)
    assert len(hits2) == 3 and c2["open_positions"].availability == "available"  # robots + home + careers fit
    assert c2["public_activity"].availability == "failed" and "budget_exhausted" in c2["public_activity"].note


def test_offsite_redirect_and_offsite_links_are_not_followed():
    def handler(req):
        if req.url.path == "/robots.txt":
            return httpx.Response(404)
        if req.url.host == "other-site.example":
            return httpx.Response(200, text="<html><body>Jobs elsewhere</body></html>", headers={"content-type": "text/html"})
        if req.url.path == "/":
            return httpx.Response(200, text=home(feed=False, news=False), headers={"content-type": "text/html"})
        return httpx.Response(302, headers={"location": "https://other-site.example/jobs"})
    f = WebFetcher(Budget(100, 15), transport=httpx.MockTransport(handler), resolver=PUBLIC, sleeper=lambda s: None)
    cs = ClaimSet()
    enrich_website(cs, OUR, "nordvik.example", f, None, today=TODAY)
    c = {x.field: x for x in cs.claims}
    assert c["open_positions"].availability == "failed" and "off the verified domain" in c["open_positions"].note


def test_nothing_is_collected_when_identity_is_not_verified():
    lookalike = home().replace("Org.nr. 910 000 012", "Org.nr. 910 000 020")
    _cs, out, hits, c = run({"/": lookalike, "/karriere": LISTING, "/feed.xml": (RSS, XML)})
    assert out.state == "ambiguous" and set(c) == {"official_website"} and "/karriere" not in hits and "/feed.xml" not in hits


def test_fabricated_item_without_page_support_is_dropped(monkeypatch):
    from signalpost.web import signals_run as sr
    fake = sg.Item("Sjef for alt", "Sjef for alt Søknadsfrist 1.1.2027", "https://nordvik.example/karriere", "listing_anchor")
    monkeypatch.setattr(sr, "jobs_from_listing", lambda *a, **k: [fake])
    _, out, _, c = run({"/": home(feed=False, news=False), "/karriere": "<html><body><h1>Karriere</h1></body></html>"})
    assert c["open_positions"].availability == "not_available"
    assert {"field": "open_positions", "value": "Sjef for alt", "method": "listing_anchor",
            "reason": "snippet not found in page"} in out.dropped


# ---------- envelope-level: validator, explanation, report, refresh ----------
FX = load("active_as_with_website")
ORG = FX["org"]
ID_HOME = ("<html><head><title>Testselskap</title>%s</head><body><h1>SYNTETISK TESTSELSKAP AS</h1>"
           "<a href=\"/karriere\">Karriere</a><a href=\"/nyheter\">Nyheter</a><footer>Testveien 1, 0150 Oslo. Org.nr 910 000 012</footer>"
           "</body></html>")


def stack(pages_ref):
    hits = []

    def handler(req):
        hits.append(req.url.path)
        if req.url.path == "/robots.txt":
            return httpx.Response(404)
        body = pages_ref[0].get(req.url.path)
        return httpx.Response(200, text=body, headers={"content-type": "text/html"}) if body else httpx.Response(404)
    f = WebFetcher(Budget(500, 50), transport=httpx.MockTransport(handler), resolver=PUBLIC, sleeper=lambda s: None)
    return f, hits


def envelope(f, store=None, now="2026-10-01T06:00:00Z", run_id="r"):
    client = ApiClient(transport=transport_for(FX), sleeper=lambda s: None)
    return register_envelope(ORG, client, run_id=run_id, fetcher=f, store=store, now=now,
                             modules=("financials", "entity", "roles", "subunits"))


JOB1 = '<ul><li><a href="/karriere/dev">Utvikler</a> Søknadsfrist 20.12.2026 Heltid</li><li><a href="/karriere/pm">Prosjektleder</a> Søknadsfrist 21.12.2026 Fast stilling</li></ul>'
NEWS1 = '<article><time datetime="2026-09-20">20.09.2026</time><h2>Vi lanserer ny tjeneste</h2></article>'


def test_envelope_is_valid_explained_and_reported():
    f, _ = stack([{"/": ID_HOME % "", "/karriere": f"<html><body>{JOB1}</body></html>", "/nyheter": f"<html><body>{NEWS1}</body></html>"}])
    env = envelope(f)
    d = json.loads(env.to_json_line())
    Envelope.model_validate(d)
    assert validate_envelope(d) == []
    c = {x["field"]: x for x in d["claims"]}
    assert c["hiring_status"]["value"] == "hiring" and len(c["open_positions"]["evidence_ids"]) == 2
    text = explain(env)
    assert "careers page lists 2 open position(s), e.g. “Utvikler”" in text and "Vi lanserer ny tjeneste" in text
    assert "2026-09-20" in text and "company's own site" in text
    page = htmlreport.render([d], {"run_id": "r"})
    assert "Hiring and public activity" in page and "Prosjektleder" in page


def test_validator_rejects_job_items_not_supported_by_their_evidence():
    f, _ = stack([{"/": ID_HOME % "", "/karriere": f"<html><body>{JOB1}</body></html>"}])
    d = json.loads(envelope(f).to_json_line())
    pos = next(c for c in d["claims"] if c["field"] == "open_positions")
    pos["value"][0]["title"] = "Helt annen stilling"
    assert any("not supported by its evidence" in p for p in validate_envelope(d))
    pos["evidence_ids"] = pos["evidence_ids"][:1]
    assert any("one evidence record per item" in p for p in validate_envelope(d))


def test_hostile_job_title_is_escaped_in_the_report():
    evil = '<ul><li><a href="/karriere/x">&lt;img src=x onerror=alert(1)&gt; Utvikler</a> Søknadsfrist 20.12.2026 Heltid</li></ul>'
    f, _ = stack([{"/": ID_HOME % "", "/karriere": f"<html><body>{evil}</body></html>"}])
    d = json.loads(envelope(f).to_json_line())
    page = htmlreport.strip_scripts(htmlreport.render([d], {"run_id": "r"}))
    assert "<img src=x" not in page and "&lt;img" in page


def test_refresh_detects_new_and_closed_jobs_and_new_activity_and_always_recrawls_volatile_pages():
    store = SnapshotStore()
    pages = [{"/": ID_HOME % "", "/karriere": f"<html><body>{JOB1}</body></html>", "/nyheter": f"<html><body>{NEWS1}</body></html>"}]
    f, hits = stack(pages)
    e1 = envelope(f, store, "2026-10-01T06:00:00Z", "r1")
    assert e1.changes == []
    hits.clear()
    e2 = envelope(f, store, "2026-10-02T06:00:00Z", "r2")  # nothing changed
    assert e2.changes == [] and "/karriere" in hits and "/nyheter" in hits  # homepage unchanged, volatile pages still re-fetched
    one_job = '<ul><li><a href="/karriere/dev">Utvikler</a> Søknadsfrist 20.12.2026 Heltid</li></ul>'
    news2 = NEWS1 + '<article><time datetime="2026-10-02">02.10.2026</time><h2>Ny kunde i Bergen</h2></article>'
    pages[0].update({"/karriere": f"<html><body>{one_job}</body></html>", "/nyheter": f"<html><body>{news2}</body></html>"})
    e3 = envelope(f, store, "2026-10-03T06:00:00Z", "r3")
    types = {ch["field"]: ch for ch in e3.changes}
    assert types["open_positions"]["change_type"] == "closed_job" and types["open_positions"]["material"] is False
    assert [r["title"] for r in types["open_positions"]["detail"]["removed"]] == ["Prosjektleder"]
    assert types["public_activity"]["change_type"] == "new_activity"
    assert types["latest_activity_date"]["new_value"] == "2026-10-02"
    pages[0]["/karriere"] = "<html><body>" + one_job + '<ul><li><a href="/karriere/qa">Testleder</a> Søknadsfrist 1.2.2027 Deltid</li></ul></body></html>'
    e4 = envelope(f, store, "2026-10-04T06:00:00Z", "r4")
    assert next(ch for ch in e4.changes if ch["field"] == "open_positions")["change_type"] == "new_job_posting"
    assert not any(ch["field"] in ("official_website", "website_description") for ch in e4.changes)  # static facts untouched


def test_group_site_naming_other_organisations_fails_closed():
    group = home().replace("Org.nr. 910 000 012.", "Org.nr. 910 000 012. Datterselskap: Nordvik Eiendom AS, org.nr. 910 000 020.")
    _cs, out, hits, c = run({"/": group, "/karriere": LISTING, "/feed.xml": (RSS, XML)})
    assert out.state == "verified" and c["official_website"].availability == "available"  # identity itself is fine
    assert c["open_positions"].availability == "ambiguous" and c["public_activity"].availability == "ambiguous"
    assert "910000020" in c["open_positions"].note and "/karriere" not in hits and "/feed.xml" not in hits
    assert "hiring_status" not in c and "careers_page" not in c
