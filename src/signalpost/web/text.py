"""Page text helpers shared by identity, extraction and the verifier."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from bs4 import BeautifulSoup

_WS = re.compile(r"\s+")
_FOLD = str.maketrans({"ø": "o", "Ø": "O", "å": "a", "Å": "A", "æ": "ae", "Æ": "AE"})


def lit(s: str) -> str:
    """Literal-comparison form: NFC, whitespace collapsed, casefolded. Punctuation is kept."""
    return _WS.sub(" ", unicodedata.normalize("NFC", s or "")).strip().casefold()


def fold(s: str) -> str:
    """Loose form for name/address matching: ascii-folded, alphanumerics only, single spaces."""
    t = unicodedata.normalize("NFKD", (s or "").translate(_FOLD)).encode("ascii", "ignore").decode().casefold()
    return _WS.sub(" ", re.sub(r"[^a-z0-9]+", " ", t)).strip()


@dataclass
class PageText:
    url: str
    text: str  # visible text, newline-separated blocks, includes header/footer
    meta: dict[str, str] = field(default_factory=dict)  # description, og:description, title
    links: list[str] = field(default_factory=list)  # absolute hrefs
    mailto: list[str] = field(default_factory=list)
    tel: list[str] = field(default_factory=list)
    jsonld: list[dict] = field(default_factory=list)
    social_hrefs: list[str] = field(default_factory=list)  # hrefs to social hosts (quotable evidence)
    anchors: list[tuple[str, str]] = field(default_factory=list)  # (absolute href, anchor text)
    feeds: list[str] = field(default_factory=list)  # RSS/Atom feeds declared in <head>
    jsonld_raw: list[str] = field(default_factory=list)  # raw JSON-LD script texts (quotable evidence)
    signal_hrefs: list[str] = field(default_factory=list)  # careers/news/portal/feed hrefs (quotable evidence)

    @property
    def corpus(self) -> str:
        """Everything a snippet may legitimately be quoted from."""
        return "\n".join([self.text, *self.meta.values(), *self.social_hrefs, *self.signal_hrefs, *self.jsonld_raw])


def parse_page(url: str, html: str) -> PageText:
    import json
    import urllib.parse

    soup = BeautifulSoup(html, "lxml")
    meta: dict[str, str] = {}
    if soup.title and soup.title.get_text(strip=True):
        meta["title"] = soup.title.get_text(" ", strip=True)
    for key, attr in (("description", {"name": "description"}), ("og:description", {"property": "og:description"}),
                      ("og:site_name", {"property": "og:site_name"})):
        tag = soup.find("meta", attrs=attr)
        if tag and tag.get("content", "").strip():
            meta[key] = tag["content"].strip()
    jsonld: list[dict] = []
    jsonld_raw: list[str] = []
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(s.string or "")
        except ValueError:
            continue
        jsonld_raw.append(s.string or "")
        jsonld.extend(x for x in (data if isinstance(data, list) else [data]) if isinstance(x, dict))
    feeds = [urllib.parse.urljoin(url, t["href"]) for t in soup.find_all("link", href=True)
             if "alternate" in (t.get("rel") or []) and any(k in (t.get("type") or "") for k in ("rss", "atom"))]
    links, mailto, tel, anchors = [], [], [], []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href and not href.lower().startswith(("mailto:", "tel:", "javascript:", "#")):
            anchors.append((urllib.parse.urljoin(url, href), re.sub(r"\s+", " ", a.get_text(" ", strip=True))[:150]))
        if href.lower().startswith("mailto:"):
            mailto.append(urllib.parse.unquote(href[7:].split("?")[0]).strip())
        elif href.lower().startswith("tel:"):
            tel.append(href[4:].strip())
        else:
            links.append(urllib.parse.urljoin(url, href))
    for t in soup(["script", "style", "noscript", "template"]):
        t.decompose()
    blocks = [_WS.sub(" ", b).strip() for b in soup.get_text("\n").split("\n")]
    text = "\n".join(b for b in blocks if b)
    social_hosts = ("linkedin.com", "facebook.com", "instagram.com", "x.com", "twitter.com", "youtube.com", "tiktok.com")
    social = [h for h in dict.fromkeys(links) if any(d in (urllib.parse.urlparse(h).hostname or "") for d in social_hosts)]
    from .signals import CAREER_RE, NEWS_RE, PORTALS
    sig_hrefs = [h for h in dict.fromkeys(links) if
                 (CAREER_RE.search(urllib.parse.urlparse(h).path) or NEWS_RE.search(urllib.parse.urlparse(h).path)
                  or any(k in (urllib.parse.urlparse(h).hostname or "") for k in PORTALS))][:60]
    return PageText(url=url, text=text, meta=meta, links=links, mailto=mailto, tel=tel, jsonld=jsonld,
                    social_hrefs=social, anchors=anchors, feeds=feeds, jsonld_raw=jsonld_raw,
                    signal_hrefs=sig_hrefs + feeds)
