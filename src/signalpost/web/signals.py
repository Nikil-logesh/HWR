"""Hiring and dated-activity extraction from the company's OWN verified website. Deterministic, precision first.

Hiring: schema.org JobPosting, listings on the careers page found through the site's own links, explicit
"no open positions" statements; external recruitment portals are only recorded as a link (never fetched).
Activity: RSS/Atom feed or news page on the same registered domain, schema.org NewsArticle/BlogPosting; an item needs
a real, parsable date. Anything not recognised is reported as not_available, never guessed.
Every item carries a literal evidence snippet that the verifier checks against the fetched page.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import urllib.parse
from dataclasses import dataclass, field
from typing import Any

from bs4 import BeautifulSoup
from lxml import etree

from .identity import core_tokens
from .text import fold

MONTHS = {m: i for i, names in enumerate([
    ("januar", "january", "jan"), ("februar", "february", "feb"), ("mars", "march", "mar"), ("april", "apr"),
    ("mai", "may"), ("juni", "june", "jun"), ("juli", "july", "jul"), ("august", "aug"),
    ("september", "sept", "sep"), ("oktober", "october", "okt", "oct"), ("november", "nov"),
    ("desember", "december", "des", "dec")], 1) for m in names}
_MON = "|".join(sorted(MONTHS, key=len, reverse=True))
DATE_RES = [
    (re.compile(r"(?<!\d)(20\d{2})-(\d{2})-(\d{2})(?!\d)"), "ymd"),
    (re.compile(r"(?<![\d.])(\d{1,2})[./-](\d{1,2})[./-](20\d{2})(?!\d)"), "dmy"),
    (re.compile(rf"(?<!\d)(\d{{1,2}})\.?\s+({_MON})\.?,?\s+(20\d{{2}})(?!\d)", re.IGNORECASE), "d_mon_y"),
    (re.compile(rf"\b({_MON})\.?\s+(\d{{1,2}}),?\s+(20\d{{2}})(?!\d)", re.IGNORECASE), "mon_d_y"),
]
PORTALS = {"webcruiter": "Webcruiter", "easycruit": "Easycruit", "jobylon": "Jobylon", "teamtailor": "Teamtailor",
           "recman": "Recman", "varbi": "Varbi", "lever.co": "Lever", "greenhouse.io": "Greenhouse",
           "workable.com": "Workable", "personio": "Personio", "hirehive": "HireHive", "jobbnorge": "Jobbnorge",
           "reachmee": "ReachMee", "jobs.lever": "Lever", "smartrecruiters": "SmartRecruiters"}
CAREER_RE = re.compile(r"karriere|jobb\b|jobbe\b|jobs?\b|careers?|ledige[-_ ]stillinger|stillinger|rekruttering|"
                       r"vacanc|work[-_ ]with[-_ ]us|bli[-_ ]med|join[-_ ]us", re.IGNORECASE)
NEWS_RE = re.compile(r"nyheter|aktuelt|\bnews\b|\bblog+\b|presse|\bpress\b|nytt\b|artikler", re.IGNORECASE)
JOB_PATH_RE = re.compile(r"/(stilling|stillinger|jobb|jobs?|karriere|careers?|vacanc\w*|position\w*|ledige[-_]stillinger)/",
                         re.IGNORECASE)
CONTEXT_RE = re.compile(r"søknadsfrist|frist|deadline|publisert|posted|ansettelsesform|fast stilling|heltid|deltid|"
                        r"full[- ]?time|part[- ]?time|sted\b|location|stillingsprosent|apply|søk\b", re.IGNORECASE)
NAV_STOP = {"les mer", "read more", "søk nå", "apply now", "alle stillinger", "se alle", "see all", "karriere",
            "jobb hos oss", "kontakt", "tilbake", "next", "previous", "home", "hjem", "flere", "mer", "more", "jobb",
            "jobs", "careers", "ledige stillinger", "open positions", "stillinger", "søk", "apply", "logg inn"}
NO_OPENINGS = re.compile(r"ingen\s+(?:ledige|åpne|aktive)\s+stillinger|ikke\s+(?:noen\s+)?ledige\s+stillinger|"
                         r"for øyeblikket\s+(?:har vi\s+)?ingen|no\s+(?:open|current|available)\s+(?:positions|vacancies|"
                         r"openings|jobs)|there are no (?:open )?(?:positions|vacancies)", re.IGNORECASE)
JOB_TYPES = {"JobPosting"}
NEWS_TYPES = {"NewsArticle", "BlogPosting", "Article", "Report", "PressRelease"}
MAX_ITEMS = 10


def parse_date(text: str, today: dt.date | None = None) -> tuple[str, str] | None:
    """First plausible date in `text` -> (ISO date, literal text). Day-first for numeric dates (Norwegian)."""
    for rx, kind in DATE_RES:
        for m in rx.finditer(text or ""):
            g = m.groups()
            try:
                if kind == "ymd":
                    y, mo, d = int(g[0]), int(g[1]), int(g[2])
                elif kind == "dmy":
                    d, mo, y = int(g[0]), int(g[1]), int(g[2])
                elif kind == "d_mon_y":
                    d, mo, y = int(g[0]), MONTHS[g[1].lower()], int(g[2])
                else:
                    mo, d, y = MONTHS[g[0].lower()], int(g[1]), int(g[2])
                return dt.date(y, mo, d).isoformat(), m.group(0)
            except (ValueError, KeyError):
                continue
    return None


def plausible_past(iso: str, today: dt.date) -> bool:
    d = dt.date.fromisoformat(iso)
    return dt.date(2000, 1, 1) <= d <= today + dt.timedelta(days=1)


@dataclass
class Item:
    title: str
    snippet: str
    page_url: str
    method: str
    url: str | None = None
    date: str | None = None  # ISO
    date_text: str | None = None
    deadline: str | None = None

    def value(self) -> dict[str, str]:
        v = {"title": self.title, "url": self.url, "date": self.date, "date_text": self.date_text,
             "deadline": self.deadline}
        return {k: x for k, x in v.items() if x}


@dataclass
class Signals:
    careers_urls: list[str] = field(default_factory=list)
    news_urls: list[str] = field(default_factory=list)
    feed_urls: list[str] = field(default_factory=list)
    portal: tuple[str, str, str] | None = None  # (portal name, href, anchor text)
    jobs: list[Item] = field(default_factory=list)
    no_openings: Item | None = None
    activity: list[Item] = field(default_factory=list)
    dropped: list[dict[str, str]] = field(default_factory=list)


def norm_url(u: str) -> str:
    p = urllib.parse.urlparse(u)
    return urllib.parse.urlunparse((p.scheme, p.netloc, p.path or "/", "", p.query, ""))


def _same_site(a: str, b: str) -> bool:
    from .fetch import registered_domain
    return registered_domain(a) == registered_domain(b)


def discover_links(base_url: str, anchors: list[tuple[str, str]], feeds: list[str]) -> Signals:
    """Candidate careers / news / feed URLs and an external portal link, from the verified site's OWN anchors."""
    sig = Signals()
    best: dict[str, list[tuple[tuple[int, int], str]]] = {"c": [], "n": []}
    for i, (href, text) in enumerate(anchors):
        p = urllib.parse.urlparse(href)
        if p.scheme not in ("http", "https"):
            continue
        host = (p.hostname or "").lower()
        portal = next((name for key, name in PORTALS.items() if key in host), None)
        if portal and sig.portal is None:
            sig.portal = (portal, href, text)
            continue
        if not _same_site(base_url, href):
            continue
        hay = f"{p.path} {text}"
        depth = len([s for s in p.path.split("/") if s])
        for key, rx in (("c", CAREER_RE), ("n", NEWS_RE)):
            if rx.search(hay):
                best[key].append(((depth, i), norm_url(href)))
    for key, target in (("c", sig.careers_urls), ("n", sig.news_urls)):
        seen: list[str] = []
        for _, u in sorted(best[key]):
            if u not in seen and u.rstrip("/") != base_url.rstrip("/"):
                seen.append(u)
        target.extend(seen[:2])
    sig.feed_urls = [u for u in dict.fromkeys(feeds) if _same_site(base_url, u)][:2]
    return sig


# ---------- hiring ----------
def _jsonld_nodes(raw_scripts: list[str]) -> list[tuple[dict[str, Any], str]]:
    out: list[tuple[dict[str, Any], str]] = []

    def walk(node: Any, raw: str) -> None:
        if isinstance(node, dict):
            out.append((node, raw))
            for v in node.values():
                walk(v, raw)
        elif isinstance(node, list):
            for v in node:
                walk(v, raw)
    for raw in raw_scripts:
        try:
            walk(json.loads(raw), raw)
        except ValueError:
            continue
    return out


def _types(node: dict[str, Any]) -> set[str]:
    t = node.get("@type")
    return {x for x in (t if isinstance(t, list) else [t]) if isinstance(x, str)}


def _raw_field(raw: str, key: str, value: str) -> str | None:
    """The literal `"key": "value"` text inside the raw JSON-LD, so the snippet is verbatim page content."""
    m = re.search(rf'"{re.escape(key)}"\s*:\s*"{re.escape(json.dumps(value, ensure_ascii=False)[1:-1])}"', raw)
    if m:
        return m.group(0)
    m = re.search(rf'"{re.escape(key)}"\s*:\s*"{re.escape(json.dumps(value)[1:-1])}"', raw)
    return m.group(0) if m else None


def org_matches(name: str | None, legal_name: str) -> bool:
    """hiringOrganization must be this company (all core legal-name tokens), else it is a recruiter/parent."""
    core = core_tokens(legal_name)
    return bool(name and core and set(core) <= set(fold(name).split()))


def jobs_from_jsonld(raw_scripts: list[str], page_url: str, legal_name: str, sig: Signals) -> list[Item]:
    items: list[Item] = []
    for node, raw in _jsonld_nodes(raw_scripts):
        if not (_types(node) & JOB_TYPES):
            continue
        title = node.get("title")
        if not isinstance(title, str) or not title.strip():
            continue
        org = node.get("hiringOrganization")
        org_name = org.get("name") if isinstance(org, dict) else org if isinstance(org, str) else None
        if not org_matches(org_name, legal_name):
            sig.dropped.append({"field": "open_positions", "value": title[:80],
                                "reason": f"hiringOrganization {org_name!r} is not this company"})
            continue
        snippet = _raw_field(raw, "title", title)
        if not snippet:
            continue
        posted = parse_date(str(node.get("datePosted") or ""))
        valid = parse_date(str(node.get("validThrough") or ""))
        url = node.get("url") if isinstance(node.get("url"), str) else None
        items.append(Item(title.strip(), snippet, page_url, "jsonld_jobposting", url,
                          posted[0] if posted else None, posted[1] if posted else None, valid[0] if valid else None))
    return items


def jobs_from_listing(html: str, page_url: str, careers_urls: list[str]) -> list[Item]:
    """Anchors under a jobs path, inside a listing context (deadline/employment words or >=2 sibling postings)."""
    soup = BeautifulSoup(html, "lxml")
    cands = []
    for a in soup.find_all("a", href=True):
        text = re.sub(r"\s+", " ", a.get_text(" ", strip=True))
        href = urllib.parse.urljoin(page_url, a["href"])
        p = urllib.parse.urlparse(href)
        if not (6 <= len(text) <= 100) or text.casefold() in NAV_STOP or not _same_site(page_url, href):
            continue
        if not JOB_PATH_RE.search(p.path + "/") or norm_url(href).rstrip("/") in {u.rstrip("/") for u in careers_urls}:
            continue
        if norm_url(href).rstrip("/") == page_url.rstrip("/"):
            continue
        ctx = text  # context = the tightest listing container (li/tr/article/div/section) of limited size
        for anc in a.find_parents(["li", "tr", "article", "div", "section"]):
            t = re.sub(r"\s+", " ", anc.get_text(" ", strip=True))
            if len(t) <= 400:
                ctx = t
                break
        cands.append((a, text, href, p, ctx))
    out: list[Item] = []
    for _a, text, href, _p, ctx in cands:
        if not CONTEXT_RE.search(ctx):  # precision first: a posting needs deadline/employment context
            continue
        dl = re.search(r"(?:søknadsfrist|frist|deadline)\D{0,12}(.{0,40})", ctx, re.IGNORECASE)
        deadline = parse_date(dl.group(1)) if dl else None
        rest = ctx.replace(deadline[1], " ") if deadline else ctx  # a posted date is not the deadline
        posted = parse_date(rest)
        out.append(Item(text, ctx[:300], page_url, "listing_anchor", norm_url(href),
                        posted[0] if posted else None, posted[1] if posted else None,
                        deadline[0] if deadline else None))
    seen, uniq = set(), []
    for it in out:
        if (it.title, it.url) not in seen:
            seen.add((it.title, it.url))
            uniq.append(it)
    return uniq[:MAX_ITEMS]


def no_openings_statement(text: str, page_url: str) -> Item | None:
    for ln in text.split("\n"):
        if NO_OPENINGS.search(ln) and len(ln) < 300:
            return Item(ln.strip(), ln.strip(), page_url, "no_openings_statement")
    return None


# ---------- dated activity ----------
def activity_from_jsonld(raw_scripts: list[str], page_url: str, today: dt.date) -> list[Item]:
    out: list[Item] = []
    for node, raw in _jsonld_nodes(raw_scripts):
        if not (_types(node) & NEWS_TYPES):
            continue
        title = node.get("headline") or node.get("name")
        pub = parse_date(str(node.get("datePublished") or node.get("dateCreated") or ""))
        if not isinstance(title, str) or not pub or not plausible_past(pub[0], today):
            continue
        key = "headline" if node.get("headline") else "name"
        snippet = _raw_field(raw, key, title)
        if snippet:
            url = node.get("url") if isinstance(node.get("url"), str) else None
            out.append(Item(title.strip(), snippet, page_url, "jsonld_article", url, pub[0], pub[1]))
    return out


def activity_from_html(html: str, page_url: str, today: dt.date) -> list[Item]:
    """Containers (article/li/div) that hold an anchor or heading AND a real date, e.g. <time datetime=...>."""
    soup = BeautifulSoup(html, "lxml")
    out: list[Item] = []
    seen_containers: set[int] = set()
    for tm in soup.find_all("time"):
        node = tm
        for _ in range(4):  # smallest ancestor that also holds a title
            node = node.parent
            if node is None or node.name in ("body", "html"):
                node = None
                break
            title_el = node.find(["h1", "h2", "h3", "h4", "a"])
            if title_el and title_el.get_text(strip=True) and id(node) not in seen_containers:
                break
        if node is None:
            continue
        seen_containers.add(id(node))
        ctx = re.sub(r"\s+", " ", node.get_text(" ", strip=True))
        raw_date = tm.get("datetime") or tm.get_text(" ", strip=True)
        pub = parse_date(raw_date) or parse_date(ctx)
        heading = node.find(["h1", "h2", "h3", "h4"]) or node.find("a")
        title = re.sub(r"\s+", " ", heading.get_text(" ", strip=True)) if heading else ""
        if not pub or not plausible_past(pub[0], today) or not (8 <= len(title) <= 200):
            continue
        anchor = heading if heading.name == "a" else heading.find("a") or node.find("a")
        url = norm_url(urllib.parse.urljoin(page_url, anchor["href"])) if anchor and anchor.get("href") else None
        iso, literal = pub
        if literal not in ctx:  # the date must be visible in the snippet, not only in a machine attribute
            visible = parse_date(ctx)
            if not visible or visible[0] != iso:  # missing or contradicting the machine date: drop (precision)
                continue
            literal = visible[1]
        out.append(Item(title, ctx[:300], page_url, "html_time_item", url, iso, literal))
    return out


def activity_from_feed(xml_text: str, feed_url: str, today: dt.date) -> list[Item]:
    parser = etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=False, recover=True)
    try:
        root = etree.fromstring(xml_text.encode("utf-8"), parser)
    except (etree.XMLSyntaxError, ValueError):
        return []
    if root is None:
        return []
    out: list[Item] = []
    for el in root.iter():
        tag = etree.QName(el).localname if isinstance(el.tag, str) else ""
        if tag not in ("item", "entry"):
            continue

        def txt(*names: str, el=el) -> str:
            for c in el:
                if isinstance(c.tag, str) and etree.QName(c).localname in names and (c.text or "").strip():
                    return c.text.strip()
            return ""
        title, when = txt("title"), txt("pubDate", "published", "updated", "date")
        link = txt("link") or next((c.get("href") for c in el if isinstance(c.tag, str)
                                    and etree.QName(c).localname == "link" and c.get("href")), "")
        pub = parse_date(when)
        if not pub:
            try:
                from email.utils import parsedate_to_datetime
                d = parsedate_to_datetime(when).date()
                pub = (d.isoformat(), when)
            except (TypeError, ValueError):
                pub = None
        if not title or not pub or not plausible_past(pub[0], today):
            continue
        raw = _raw_chunk(xml_text, title, when)
        if raw:
            out.append(Item(title, raw, feed_url, "rss_item", urllib.parse.urljoin(feed_url, link) if link else None,
                            pub[0], when))
    return out


def _raw_chunk(xml_text: str, title: str, when: str) -> str | None:
    """Verbatim slice of the feed that contains both the title and the date (so the snippet is literal)."""
    i = xml_text.find(title)
    if i < 0 or when not in xml_text:
        return None
    start = xml_text.rfind("<", 0, max(0, i - 40)) if i > 40 else 0
    j = xml_text.find(when, max(0, i - 600))
    if j < 0:
        return None
    end = min(len(xml_text), max(i + len(title), j + len(when)) + 12)
    chunk = xml_text[min(start, i):end]
    return chunk if len(chunk) <= 900 and title in chunk and when in chunk else None
