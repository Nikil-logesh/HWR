"""Fetch careers / news / feed pages of an identity-verified site, extract hiring + dated activity, verify, publish."""
from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from ..claims import ClaimSet
from ..universe import valid_orgnr
from .fetch import Page, WebFetcher, registered_domain
from .identity import ORG_NUM, CompanyIdentity
from .signals import (
    MAX_ITEMS,
    Item,
    Signals,
    activity_from_feed,
    activity_from_html,
    activity_from_jsonld,
    discover_links,
    jobs_from_jsonld,
    jobs_from_listing,
    no_openings_statement,
    norm_url,
)
from .text import PageText, lit, parse_page
from .verify import Candidate, verify

if TYPE_CHECKING:
    from .enrich import WebOutcome

SRC = "company_owned_website"
CONF = {"jsonld_jobposting": 0.9, "rss_item": 0.9, "jsonld_article": 0.9, "listing_anchor": 0.8,
        "html_time_item": 0.8, "no_openings_statement": 0.85}


def _evidence(item: Item, pages: dict[str, Page]) -> dict[str, str | None]:
    pg = pages[item.page_url]
    return {"source_url": pg.final_url, "retrieved_at": pg.retrieved_at, "sha256": pg.sha256, "span": item.snippet[:600],
            "method": item.method}


def collect_and_publish(cs: ClaimSet, ident: CompanyIdentity, home: Page, pages: list[tuple[Page, PageText]],
                        fetcher: WebFetcher, out: WebOutcome, identity_score: float, today: dt.date,
                        homepage_only: bool = False) -> None:
    texts = {t.url: t for _, t in pages}
    page_by_url = {p.final_url: p for p, _ in pages}
    # Scope guard: a site that also names OTHER organisation numbers may be a group/parent site. Its jobs and news
    # describe the group, not necessarily this legal entity, so hiring and activity fail closed (ambiguous).
    others = sorted({d for t in texts.values() for m in ORG_NUM.finditer(t.corpus)
                     if valid_orgnr(d := "".join(m.groups())) and d != ident.org})
    if others:
        note = (f"not published: the verified site also names other organisation numbers ({', '.join(others[:3])}), "
                "so jobs and news may belong to a group or another entity")
        for field_name in ("open_positions", "public_activity"):
            cs.unavailable(field_name, "ambiguous", note=note)
        return
    corpus = {u: t.corpus for u, t in texts.items()}
    home_pt = next(iter(texts.values()))
    sig: Signals = discover_links(home.final_url, home_pt.anchors, home_pt.feeds)
    state: dict[str, str] = {}  # what happened to each source kind: ok / blocked / failed:<why> / absent

    def fetch(url: str, kind: str, feed: bool = False) -> Page | None:
        if homepage_only:
            state[kind] = "skipped: robots.txt unreachable, homepage only"
            return None
        ok, used = fetcher.robots_allows(url, ident.org)
        out.requests += used
        if ok is False:
            state[kind] = "blocked: robots.txt"
            return None
        pg = fetcher.page(url, ident.org, home_domain=registered_domain(home.final_url), accept_xml=feed)
        out.requests += pg.requests
        if not pg.ok or pg.redirected_offsite:
            state[kind] = f"failed: {pg.error or 'redirected off the verified domain'}"
            return None
        page_by_url[pg.final_url] = pg
        corpus[pg.final_url] = pg.html if feed else ""
        state[kind] = "ok"
        return pg

    careers_pt: PageText | None = None
    if sig.careers_urls:
        pg = fetch(sig.careers_urls[0], "careers")
        if pg:
            careers_pt = parse_page(pg.final_url, pg.html)
            texts[pg.final_url] = careers_pt
            corpus[pg.final_url] = careers_pt.corpus
    feed_items: list[Item] = []
    if sig.feed_urls:
        pg = fetch(sig.feed_urls[0], "feed", feed=True)
        if pg:
            feed_items = activity_from_feed(pg.html, pg.final_url, today)
    news_pt: PageText | None = None
    if not feed_items and sig.news_urls:
        pg = fetch(sig.news_urls[0], "news")
        if pg:
            news_pt = parse_page(pg.final_url, pg.html)
            texts[pg.final_url] = news_pt
            corpus[pg.final_url] = news_pt.corpus

    # ---- extraction ----
    jobs: list[Item] = []
    for pt in texts.values():
        jobs += jobs_from_jsonld(pt.jsonld_raw, pt.url, ident.name, sig)
    no_open: Item | None = None
    if careers_pt is not None:
        html = page_by_url[careers_pt.url].html
        jobs += jobs_from_listing(html, careers_pt.url, sig.careers_urls)
        no_open = no_openings_statement(careers_pt.text, careers_pt.url)
    activity = list(feed_items)
    for pt in texts.values():
        activity += activity_from_jsonld(pt.jsonld_raw, pt.url, today)
        if pt is news_pt or pt is home_pt:
            activity += activity_from_html(page_by_url[pt.url].html, pt.url, today)

    def verified(items: list[Item], field: str) -> list[Item]:
        keep, seen = [], set()
        for it in items:
            key = (it.title.casefold(), it.date or "")
            if key in seen:
                continue
            ok, reason = verify(Candidate(field, it.title, it.snippet, it.page_url, it.method), corpus)
            if ok and it.date_text and lit(it.date_text) not in lit(corpus.get(it.page_url, "")):
                ok, reason = False, "date text not found in page"
            if not ok:
                out.dropped.append({"field": field, "value": it.title[:80], "method": it.method, "reason": reason})
                continue
            seen.add(key)
            keep.append(it)
        return keep

    jobs = verified(jobs, "open_positions")[:MAX_ITEMS]
    activity = sorted(verified(activity, "public_activity"), key=lambda i: (i.date or "", i.title), reverse=True)[:MAX_ITEMS]
    for d in sig.dropped:
        out.dropped.append({**d, "method": "jsonld_jobposting"})

    # ---- publish: careers page / open positions / hiring status ----
    conf = lambda it: min(CONF.get(it.method, 0.8), identity_score)
    careers_url = careers_pt.url if careers_pt else (sig.careers_urls[0] if sig.careers_urls else None)
    if careers_url or sig.portal:
        kind, portal = ("company_page", None) if careers_url else ("external_portal", sig.portal[0] if sig.portal else None)
        href = careers_url or sig.portal[1]
        quoted = next((h for h in home_pt.signal_hrefs if norm_url(h) == norm_url(href)), None)
        if quoted:  # the link as written on the verified homepage is the evidence
            val = {"url": href, "kind": kind, **({"portal": portal} if portal else {})}
            cs.available("careers_page", val, confidence=min(0.9, identity_score), source_url=home.final_url,
                         source_class=SRC, retrieved_at=home.retrieved_at, sha256=home.sha256, span=quoted,
                         method="linked_from_verified_homepage")
            out.published += 1
    if jobs:
        cs.available_items("open_positions", [j.value() for j in jobs], [_evidence(j, page_by_url) for j in jobs],
                           confidence=min(conf(j) for j in jobs), source_class=SRC,
                           note="listed on the company's own site; not verified against the job's own page")
        cs.available("hiring_status", "hiring", confidence=min(conf(j) for j in jobs), source_url=page_by_url[jobs[0].page_url].final_url,
                     source_class=SRC, retrieved_at=page_by_url[jobs[0].page_url].retrieved_at,
                     sha256=page_by_url[jobs[0].page_url].sha256, span=jobs[0].snippet[:600], method=jobs[0].method)
        out.published += 2
    elif no_open and verified([no_open], "open_positions"):
        pg = page_by_url[no_open.page_url]
        cs.unavailable("open_positions", "not_available", note="the careers page states there are no open positions",
                       source_url=pg.final_url, source_class=SRC, retrieved_at=pg.retrieved_at, sha256=pg.sha256,
                       method="no_openings_statement")
        cs.available("hiring_status", "no_open_positions", confidence=min(CONF["no_openings_statement"], identity_score),
                     source_url=pg.final_url, source_class=SRC, retrieved_at=pg.retrieved_at, sha256=pg.sha256,
                     span=no_open.snippet[:600], method="no_openings_statement")
        out.published += 1
    else:
        why = {"blocked": "robots.txt forbids fetching the careers page", "failed": "the careers page could not be fetched"}
        st = state.get("careers", "")
        if st.startswith("blocked"):
            cs.unavailable("open_positions", "blocked", note=why["blocked"])
        elif st.startswith("failed"):
            cs.unavailable("open_positions", "failed", note=f"{why['failed']} ({st})")
        elif careers_pt is not None:
            cs.unavailable("open_positions", "not_available", note="careers page fetched; no job listings recognised")
        elif sig.portal:
            cs.unavailable("open_positions", "not_available",
                           note=f"recruitment is handled on an external portal ({sig.portal[0]}); not fetched")
        else:
            cs.unavailable("open_positions", "not_available",
                           note="no careers or jobs page is linked from the verified website")
    # ---- publish: dated activity ----
    if activity:
        cs.available_items("public_activity", [a.value() for a in activity], [_evidence(a, page_by_url) for a in activity],
                           confidence=min(conf(a) for a in activity), source_class=SRC, as_of=activity[0].date,
                           note="dated items published on the company's own site")
        top = activity[0]
        pg = page_by_url[top.page_url]
        cs.available("latest_activity_date", top.date, confidence=conf(top), source_url=pg.final_url, source_class=SRC,
                     retrieved_at=pg.retrieved_at, sha256=pg.sha256, span=top.snippet[:600], method=top.method,
                     as_of=top.date)
        out.published += 2
        return
    tried = {k: v for k, v in state.items() if k in ("feed", "news")}
    if tried and all(v.startswith("blocked") for v in tried.values()):
        cs.unavailable("public_activity", "blocked", note="; ".join(f"{k}: {v}" for k, v in tried.items()))
    elif tried and all(v != "ok" for v in tried.values()):
        cs.unavailable("public_activity", "failed", note="; ".join(f"{k}: {v}" for k, v in tried.items()))
    else:
        checked = [u for u, k in ((sig.feed_urls[0] if sig.feed_urls else None, "feed"),
                                  (sig.news_urls[0] if sig.news_urls else None, "news")) if u and tried.get(k) == "ok"]
        cs.unavailable("public_activity", "not_available",
                       note=("no dated items recognised on " + ", ".join(checked)) if checked
                       else "no news page, feed or dated items found on the verified website")
