"""Deterministic candidate extraction (no LLM) + LLM candidate proposal. All candidates go through verify()."""
from __future__ import annotations

import re

from norway_company_agent.identity import assess_social_identity
from norway_company_agent.website import normalize_social_url

from .fetch import registered_domain
from .identity import GENERIC_TOKENS, CompanyIdentity, core_tokens, street_variants
from .signals import parse_date
from .text import PageText, fold
from .verify import Candidate

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Norwegian numbers: 8 digits as 2-2-2-2 or 3-2-3, optional +47/0047; single spaces only (dots made dates look like phones).
# A "+" or a further digit group directly in front/behind means a longer or foreign number, never a Norwegian 8-digit one.
PHONE = re.compile(r"(?<![\d@+])(?<!\d[./-])(?:\+ ?47 ?|0047 ?)?(?:\d{2} ?\d{2} ?\d{2} ?\d{2}|\d{3} ?\d{2} ?\d{3})(?!\d)(?![./-]\d)"
                   r"(?! \d{2,3}(?!\d))")
FOREIGN_PREFIX = re.compile(r"(?:\+|\b00)\s?\(?(\d{2,3})\)?\s?\(?0?\)?[\s.-]?$")
NOT_PHONE_LABEL = re.compile(r"org\.?\s?(?:nr|nummer|no)|organisasjons|\bbank|\bkonto(?:nr|nummer)?\b|iban|swift|\bkid\b|\bmva\b|fødsels|postboks|"
                             r"faks|fax|kundenr|saksnr|ordrenr|fakturanr|ref\.?\s?nr", re.IGNORECASE)
FAX = re.compile(r"\bfaks?\b|\bfax\b", re.IGNORECASE)
BAD_LOCAL = re.compile(r"fornavn|etternavn|firstname|lastname|first\.last|dinepost|din\.epost|example|eksempel|"
                       r"no-?reply|do-?not-?reply|faktura|invoice|regnskap|billing|^(name|navn|test|epost|mail|email|user|brukernavn|xxx+|din)$",
                       re.IGNORECASE)
GENERIC_LOCAL = {"post", "info", "kontakt", "kontoret", "contact", "hello", "hei", "mail", "epost", "e-post", "firmapost",
                 "office", "kundeservice", "support", "salg", "sales", "booking", "styret", "resepsjon", "admin"}
FREEMAIL = {"gmail.com", "hotmail.com", "hotmail.no", "outlook.com", "outlook.no", "live.com", "live.no", "icloud.com",
            "me.com", "yahoo.com", "yahoo.no", "msn.com", "online.no", "broadpark.no", "getmail.no", "start.no",
            "frisurf.no", "c2i.net", "bbnett.no", "lyse.net", "altibox.no", "proton.me", "protonmail.com", "tele2.no",
            "combo.no", "sol.no", "mac.com", "gmx.com", "gmx.net", "aol.com", "hotmail.co.uk"}
HOME_TLDS = {"no", "com", "org", "net", "eu", "io", "as"}
MARKUP = re.compile(r"</?[a-zA-Z][^>]*>")
LLM_CHARS = 6000


def _line_with(text: str, needle: str) -> str | None:
    for ln in text.split("\n"):
        if needle in ln:
            return ln.strip()
    return None


WINDOW_BEFORE, WINDOW_AFTER = 160, 100  # characters (folded) in which a name/address/org number is "next to" a contact
POBOX = re.compile(r"(?:postboks|pb\.?|box)\s*\d+,?\s+\d{4}\s+[A-ZÆØÅ][A-Za-zÆØÅæøå-]+", re.IGNORECASE)
POSTCITY = re.compile(r"(?<![\d+/.-])(\d{4})\s+[A-ZÆØÅ][A-Za-zÆØÅæøå-]{2,}")  # not a fragment of a longer number
NOT_ADDRESS = re.compile(r"(?:©|\(c\)|copyright)\s*(?:©\s*)?\d{4}", re.IGNORECASE)  # "© 2026 Nordvik" is a year, not a postcode


def _addresses_only(text: str) -> str:
    """Page text without postbox lines and copyright years, which look like addresses but name no unit."""
    return NOT_ADDRESS.sub(" ", POBOX.sub(" ", text))


def nearest_unit(text: str, value: str, name: str, org: str | None, ident: CompanyIdentity | None) -> str | None:
    """Whose name or address the contact belongs to: "own", "other" (another postcode/city) or None (nothing near).
    A value shown several times is judged on its best occurrence: own beats other beats nothing."""
    text = _addresses_only(text)
    folded = fold(text)
    own_pc = ident.postcode if ident else None
    marks: list[tuple[int, str]] = []
    # the full legal name (with its AS/ANS/...) is own; the bare core name also starts sister names ("Nordvik Bygg Sør Inc.")
    for n in [fold(name), *street_variants(ident.street if ident else None)]:
        if n:
            marks += [(m.start(), "own") for m in re.finditer(rf"(?<![a-z0-9]){re.escape(n)}(?![a-z0-9])", folded)]
    marks += [(m.start(), "own" if m.group(1) == own_pc else "other") for m in re.finditer(r"(?<!\d)(\d{4}) [a-z]{3,}", folded)]
    if org:
        marks += [(m.start(), "own") for m in re.finditer(r"(?<!\d)(\d{3}) ?(\d{3}) ?(\d{3})(?!\d)", folded) if "".join(m.groups()) == org]
    verdicts: set[str] = set()
    for occ in re.finditer(re.escape(value), text):
        pos = len(fold(text[:occ.start()]))
        # Unit blocks read "name / address / contact person / tel / mail": a contact belongs to the unit that precedes it.
        before = [(pos - p, who) for p, who in marks if 0 <= pos - p <= WINDOW_BEFORE]
        after = [(p - pos, who) for p, who in marks if 0 < p - pos <= WINDOW_AFTER]
        if before:
            verdicts.add(min(before)[1])
        elif after:
            verdicts.add(min(after)[1])
    return "own" if "own" in verdicts else "other" if "other" in verdicts else None


def multi_location(text: str, own_postcode: str | None) -> bool:
    """A page that gives addresses in several other postcodes lists sister units or branches; its phones and mailboxes
    belong to whichever unit they sit next to, not automatically to the company we are profiling."""
    return len({m for m in POSTCITY.findall(_addresses_only(text)) if m != own_postcode}) >= 2


def _block_around(text: str, needle: str, radius: int = 1) -> str:
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if needle in ln:
            return "\n".join(lines[max(0, i - radius): i + radius + 1])
    return ""


def domain_names_company(domain: str, company_name: str) -> bool:
    """The mail domain's label contains a distinctive word of the legal name (skeisbotnen.no for SKEISBOTNEN BARNEHAGE AS)."""
    if domain.rsplit(".", 1)[-1] not in HOME_TLDS:  # nordnet.se is the Swedish parent, not the Norwegian branch
        return False
    label = re.sub(r"[^a-z0-9]", "", fold(registered_domain(f"http://{domain}/") or domain).split(" ")[0] if domain else "")
    return len(label) >= 4 and any(len(t) >= 4 and t not in GENERIC_TOKENS and t in label for t in core_tokens(company_name))


def email_verdict(email: str, page_url: str, text: str, company_name: str, org: str | None,
                  ident: CompanyIdentity | None = None) -> str | None:
    """None = acceptable; otherwise the reason it is not attributed to this company."""
    local, _, domain = email.partition("@")
    domain = domain.lower()
    if BAD_LOCAL.search(local):
        return "placeholder, no-reply or invoicing mailbox"
    if domain in FREEMAIL or registered_domain(f"http://{domain}/") == registered_domain(page_url):
        return None
    if domain_names_company(domain, company_name):
        return None
    block = fold(_block_around(text, email))
    core = " ".join(core_tokens(company_name))
    if (core and re.search(rf"(?<![a-z0-9]){re.escape(core)}(?![a-z0-9])", block)) or (org and org in re.sub(r"\D", "", block)):
        return None
    return "email domain differs from the site and is not next to the company name"


def phone_verdict(match: re.Match[str], text: str) -> str | None:
    raw = match.group(0).strip()
    if parse_date(raw):
        return "looks like a date"
    ls = text.rfind("\n", 0, match.start()) + 1
    left = text[ls: match.start()][-28:]
    foreign = FOREIGN_PREFIX.search(left)
    if foreign and foreign.group(1) != "47":
        return f"foreign country code +{foreign.group(1)}"
    if NOT_PHONE_LABEL.search(left):
        return "labelled as an organisation/bank/fax/reference number"
    return None


def description_verdict(desc: str) -> str | None:
    """None = reads like a description; otherwise why it is not one (an address block, markup, a bare call to action)."""
    if MARKUP.search(desc):
        return "markup inside the description"
    if EMAIL.search(desc) or PHONE.search(desc) or re.search(r"\b(?:tlf|tel|telefon|e-?post)\b[.:]", desc, re.IGNORECASE):
        return "contact details, not a description"
    return None


def deterministic_candidates(pages: list[PageText], company_name: str, org: str | None = None,
                             dropped: list[dict[str, str]] | None = None, ident: CompanyIdentity | None = None) -> list[Candidate]:
    out: list[Candidate] = []
    seen: set[tuple[str, str]] = set()

    def add(c: Candidate) -> None:
        # one phone number is one fact however it is spaced; the first (page-order) rendering is kept
        key = (c.field, re.sub(r"\D", "", c.value)[-8:] if c.field == "contact_phone" else c.value.casefold())
        if key not in seen:
            seen.add(key)
            out.append(c)

    def drop(field: str, value: str, reason: str) -> None:
        if dropped is not None:
            dropped.append({"field": field, "value": value[:80], "method": "deterministic", "reason": reason})

    for pg in pages:
        desc = pg.meta.get("description") or pg.meta.get("og:description")
        if desc and len(desc) >= 30:
            why = description_verdict(desc)
            if why:
                drop("website_description", desc, why)
            else:
                add(Candidate("website_description", desc, desc, pg.url, "meta_description"))
        contacts: list[tuple[Candidate, str | None]] = []  # (candidate, whose address/name is nearest on this page)
        emails = {m for m in pg.mailto if EMAIL.fullmatch(m)} | set(EMAIL.findall(pg.text))
        # shared mailboxes (post@, info@ ...) before personal ones: they are the company's contact, a named colleague is not
        for em in sorted(emails, key=lambda e: (e.partition("@")[0].lower() not in GENERIC_LOCAL, e.lower())):
            ln = _line_with(pg.text, em)
            if not ln:
                continue
            why = email_verdict(em, pg.url, pg.text, company_name, org, ident)
            if why:
                drop("contact_email", em, why)
            else:
                contacts.append((Candidate("contact_email", em, ln, pg.url, "visible_email"), nearest_unit(pg.text, em, company_name, org, ident)))
        for m in PHONE.finditer(pg.text):
            ln = _line_with(pg.text, m.group(0))
            if not ln or FAX.search(ln):
                continue
            why = phone_verdict(m, pg.text)
            if why:
                drop("contact_phone", m.group(0), why)
            else:
                contacts.append((Candidate("contact_phone", m.group(0).strip(), ln, pg.url, "visible_phone"),
                                 nearest_unit(pg.text, m.group(0), company_name, org, ident)))
        # Whose contact is it? A page that has a block for this company (its name/street/org number next to a contact)
        # gets only those contacts; a page listing several other locations gets none it cannot tie to this company.
        has_own = any(u == "own" for _, u in contacts)
        multi = multi_location(pg.text, ident.postcode if ident else None)
        for c, unit in contacts:
            if has_own and unit != "own":
                drop(c.field, c.value, "this page has a block for the company and the contact is not in it")
            elif multi and unit != "own":
                drop(c.field, c.value, "page lists several other locations and this contact is not next to this company's name or address")
            else:
                add(c)
        for href in pg.social_hrefs:
            norm = normalize_social_url(href)
            if not norm:
                continue
            res = assess_social_identity({"name": company_name}, norm)
            if res["publishable"]:
                # value is the href exactly as published, so the verifier can match it literally
                # tracking parameters are not part of the profile address; the snippet keeps the link exactly as published
                add(Candidate(f"social_{norm['platform']}", re.split(r"[?#]", href)[0], href, pg.url, "linked_social_profile"))
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
