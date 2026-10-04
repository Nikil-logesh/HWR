"""Website enrichment for one company. Fails closed: low identity => no web facts at all."""
from __future__ import annotations

import datetime as dt
import urllib.parse
from dataclasses import dataclass, field

from ..claims import ClaimSet
from ..models import Envelope
from .extract import deterministic_candidates, llm_candidates, llm_prompt
from .fetch import Page, WebFetcher, registered_domain
from .identity import CompanyIdentity, IdentityResult, assess
from .llm import LlmClient
from .safe import normalize_homepage
from .signals_run import collect_and_publish
from .text import PageText, lit, parse_page
from .verify import verify

SRC = "company_owned_website"
PRIORITY = ("om-oss", "om_oss", "omoss", "about", "kontakt", "contact")
MAX_SECONDARY = 2
CONF_FACT = {"meta_description": 0.85, "visible_email": 0.85, "visible_phone": 0.85, "linked_social_profile": 0.85,
             "llm": 0.75}


@dataclass
class WebOutcome:
    state: str  # no_website | blocked | failed | not_available | ambiguous | verified
    requests: int = 0
    identity: IdentityResult | None = None
    dropped: list[dict] = field(default_factory=list)
    published: int = 0
    homepage_sha: str | None = None
    skipped_unchanged: bool = False


def _secondary_urls(home: Page, pt: PageText) -> list[str]:
    base_dom = registered_domain(home.final_url)
    ranked: dict[str, int] = {}
    for href in pt.links:
        p = urllib.parse.urlparse(href)
        if p.scheme not in ("http", "https") or registered_domain(href) != base_dom:
            continue
        hay = p.path.casefold()
        rank = next((i for i, t in enumerate(PRIORITY) if t in hay), None)
        clean = urllib.parse.urlunparse((p.scheme, p.netloc, p.path or "/", "", "", ""))
        if rank is not None and clean.rstrip("/") != home.final_url.rstrip("/"):
            ranked[clean] = min(rank, ranked.get(clean, rank))
    return [u for u, _ in sorted(ranked.items(), key=lambda kv: (kv[1], kv[0]))][:MAX_SECONDARY]


def _today() -> dt.date:
    return dt.datetime.now(dt.UTC).date()


WEB_FIELDS = ("official_website", "website_description", "contact_email", "contact_phone", "social_",
              "products_services")


def enrich_website(cs: ClaimSet, ident: CompanyIdentity, registry_website: str | None, fetcher: WebFetcher,
                   llm: LlmClient | None = None, *, prior_sha: str | None = None,
                   previous: Envelope | None = None, capture: list[PageText] | None = None,
                   today: dt.date | None = None) -> WebOutcome:
    url = normalize_homepage(registry_website)
    if not url:  # normal, fast path: zero requests
        cs.unavailable("official_website", "not_available", note="no website listed in the official register; "
                       "no search-based discovery performed")
        return WebOutcome("no_website")
    out = WebOutcome("failed")
    allowed, used = fetcher.robots_allows(url, ident.org)
    out.requests += used
    if allowed is False:
        cs.unavailable("official_website", "blocked", note="robots.txt disallows fetching the registered website")
        out.state = "blocked"
        return out
    home = fetcher.page(url, ident.org)
    out.requests += home.requests
    if not home.ok:
        if home.status in (404, 410):
            cs.unavailable("official_website", "not_available", note=f"registered website returned HTTP {home.status}",
                           source_url=url, source_class=SRC, retrieved_at=home.retrieved_at)
            out.state = "not_available"
        elif home.status in (401, 403, 429, -2):
            cs.unavailable("official_website", "blocked", note=f"website refused or unsafe: {home.error}")
            out.state = "blocked"
        else:
            cs.unavailable("official_website", "failed", note=f"website fetch failed: {home.error}")
        return out

    out.homepage_sha = home.sha256
    if prior_sha and prior_sha == home.sha256 and previous is not None:
        prior = [c for c in previous.claims if c.field.startswith(WEB_FIELDS)]
        if any(c.field == "official_website" and c.availability == "available" for c in prior):
            # source unchanged since the last verified run: reuse its verified claims, skip secondary pages + LLM
            cs.claims.extend(cs.carry(c, previous) for c in prior)
            out.state, out.skipped_unchanged = "verified", True
            site = next(c for c in prior if c.field == "official_website")
            # jobs and news change far more often than the homepage: always re-collect them
            collect_and_publish(cs, ident, home, [(home, parse_page(home.final_url, home.html))], fetcher, out,
                                site.confidence, today or _today(), homepage_only=allowed is None)
            return out
    pages: list[tuple[Page, PageText]] = [(home, parse_page(home.final_url, home.html))]
    if allowed is not None:  # unreachable robots.txt => homepage only
        for u in _secondary_urls(home, pages[0][1]):
            ok, used = fetcher.robots_allows(u, ident.org)
            out.requests += used
            if ok is False:
                continue
            pg = fetcher.page(u, ident.org, home_domain=registered_domain(home.final_url))
            out.requests += pg.requests
            if pg.ok and not pg.redirected_offsite:
                pages.append((pg, parse_page(pg.final_url, pg.html)))
    texts = [t for _, t in pages]
    res = assess(ident, texts)
    out.identity = res
    if not res.publishable:
        why = res.veto or f"identity score {res.score:.2f} below 0.90 (signals: {', '.join(res.signals) or 'none'})"
        cs.unavailable("official_website", "ambiguous", note=f"not published: {why}", source_url=home.final_url,
                       source_class=SRC, retrieved_at=home.retrieved_at, sha256=home.sha256, method="identity_gate")
        out.state = "ambiguous"
        return out

    holder = next(((p, t) for p, t in pages if res.snippet and lit(res.snippet) in lit(t.corpus)), pages[0])
    cs.available("official_website", home.final_url, confidence=res.score, source_url=holder[0].final_url,
                 source_class=SRC, retrieved_at=holder[0].retrieved_at, sha256=holder[0].sha256,
                 span=res.snippet or ident.name, method="identity_gate:" + "+".join(res.signals))
    out.state = "verified"
    if capture is not None:  # model benchmark: the identity-verified pages exactly as the LLM would see them
        capture.extend(texts)

    by_url = {p.final_url: p for p, _ in pages}
    corpus = {t.url: t.corpus for t in texts}
    cands = deterministic_candidates(texts, ident.name, ident.org, out.dropped)
    have_desc = any(c.field == "website_description" for c in cands)
    if llm and llm.enabled:
        cands += [c for c in llm_candidates(llm.complete_json(llm_prompt(texts), ident.org), texts)
                  if not (have_desc and c.field == "website_description")]
    caps = {"contact_email": 3, "contact_phone": 2, "products_services": 8}
    counts: dict[str, int] = {}
    svc: list = []
    for c in cands:
        ok, reason = verify(c, corpus)
        if not ok:
            out.dropped.append({"field": c.field, "value": c.value[:80], "method": c.method, "reason": reason})
            continue
        if counts.get(c.field, 0) >= caps.get(c.field, 1):
            continue
        pg = by_url[c.page_url]
        field_name = c.field
        if field_name == "products_services":  # multi-valued: collect into one claim below
            counts[field_name] = counts.get(field_name, 0) + 1
            svc.append((c, pg))
            continue
        if field_name in ("contact_email", "contact_phone"):
            field_name = f"{c.field}_{counts.get(c.field, 0) + 1}"
        counts[c.field] = counts.get(c.field, 0) + 1
        cs.available(field_name, c.value, confidence=min(CONF_FACT[c.method], res.score), source_url=pg.final_url,
                     source_class=SRC, retrieved_at=pg.retrieved_at, sha256=pg.sha256, span=c.snippet[:600],
                     method=c.method)
        out.published += 1
    if svc:
        pg = by_url[svc[0][0].page_url]
        cs.available("products_services", [c.value for c, _ in svc], confidence=CONF_FACT["llm"],
                     source_url=pg.final_url, source_class=SRC, retrieved_at=pg.retrieved_at, sha256=pg.sha256,
                     span=" | ".join(c.snippet for c, _ in svc)[:1500], method="llm")
        out.published += 1
    collect_and_publish(cs, ident, home, pages, fetcher, out, res.score, today or _today(),
                        homepage_only=allowed is None)
    return out
