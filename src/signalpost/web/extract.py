"""Deterministic candidate extraction (no LLM) + LLM candidate proposal. All candidates go through verify()."""
from __future__ import annotations

import re

from norway_company_agent.identity import assess_social_identity
from norway_company_agent.website import normalize_social_url

from .text import PageText
from .verify import Candidate

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<![\d@])(?:\+47[ .]?|0047[ .]?)?(?:\d{2}[ .]?\d{2}[ .]?\d{2}[ .]?\d{2}|\d{3}[ .]?\d{2}[ .]?\d{3})(?!\d)")
FAX = re.compile(r"\bfaks?\b|\bfax\b", re.IGNORECASE)
LLM_CHARS = 6000


def _line_with(text: str, needle: str) -> str | None:
    for ln in text.split("\n"):
        if needle in ln:
            return ln.strip()
    return None


def deterministic_candidates(pages: list[PageText], company_name: str) -> list[Candidate]:
    out: list[Candidate] = []
    seen: set[tuple[str, str]] = set()

    def add(c: Candidate) -> None:
        key = (c.field, c.value.casefold())
        if key not in seen:
            seen.add(key)
            out.append(c)

    for pg in pages:
        desc = pg.meta.get("description") or pg.meta.get("og:description")
        if desc and len(desc) >= 30:
            add(Candidate("website_description", desc, desc, pg.url, "meta_description"))
        emails = {m for m in pg.mailto if EMAIL.fullmatch(m)} | set(EMAIL.findall(pg.text))
        for em in sorted(emails):
            ln = _line_with(pg.text, em)
            if ln:
                add(Candidate("contact_email", em, ln, pg.url, "visible_email"))
        for m in PHONE.finditer(pg.text):
            ln = _line_with(pg.text, m.group(0))
            if ln and not FAX.search(ln):
                add(Candidate("contact_phone", m.group(0).strip(), ln, pg.url, "visible_phone"))
        for href in pg.social_hrefs:
            norm = normalize_social_url(href)
            if not norm:
                continue
            res = assess_social_identity({"name": company_name}, norm)
            if res["publishable"]:
                # value is the href exactly as published, so the verifier can match it literally
                add(Candidate(f"social_{norm['platform']}", href, href, pg.url, "linked_social_profile"))
    return out


def llm_prompt(pages: list[PageText]) -> str:
    parts, used = [], 0
    for i, pg in enumerate(pages, 1):
        chunk = pg.text[: max(0, LLM_CHARS - used)]
        if not chunk:
            break
        used += len(chunk)
        parts.append(f"[PAGE {i}] {pg.url}\n{chunk}")
    return ("Extract from the pages below. JSON schema: "
            '{"description": {"page": int, "value": str, "evidence_snippet": str} | null, '
            '"services": [{"page": int, "value": str, "evidence_snippet": str}]}. '
            "description = one sentence that says what the company does. services = up to 6 products/services "
            "named on the page. value and evidence_snippet are verbatim page text.\n\n" + "\n\n".join(parts))


def llm_candidates(data: dict | None, pages: list[PageText]) -> list[Candidate]:
    if not isinstance(data, dict):
        return []
    out: list[Candidate] = []

    def one(field: str, item) -> None:
        if not isinstance(item, dict):
            return
        try:
            page = pages[int(item.get("page", 1)) - 1]
        except (ValueError, TypeError, IndexError):
            return
        v, sn = item.get("value"), item.get("evidence_snippet")
        if isinstance(v, str) and isinstance(sn, str):
            out.append(Candidate(field, v, sn, page.url, "llm"))

    one("website_description", data.get("description"))
    for it in (data.get("services") or [])[:8]:
        one("products_services", it)
    return out
