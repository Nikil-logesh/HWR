"""Identity gate: does this page belong to THIS legal entity? Computed in code, never by an LLM.

Publish threshold 0.90. Signals (best applicable wins):
  1.00  exact organisation number on the page
  0.95  full legal name + exact street address (street + number)
  0.92  full legal name + postcode and city together / registered phone number
  0.70  legal name + municipality only  (review, NOT publishable)
  0.50  legal name only                 (NOT publishable)
Vetoes: a different valid organisation number given as the company's number; parked/for-sale pages.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..universe import valid_orgnr
from .text import PageText, fold

PUBLISH_THRESHOLD = 0.90
LEGAL_FORMS = {"as", "asa", "ans", "da", "enk", "iks", "sa", "sam", "sti", "nuf", "ks", "brl", "bbl", "fli", "esek",
               "spa", "stiftelsen", "stiftelse"}
PARKED = ("domain is for sale", "domain for sale", "hugedomains", "this domain may be for sale",
          "buy this domain", "domene til salgs", "parked domain", "sedo domain parking")
GROUP_LIST_LIMIT = 2
ENTITY_BEFORE = re.compile(r"(?:\b(?:AS|ASA|SA|ANS|DA|KS|IKS|NUF|BA)|borettslag|sameie|stiftelse)\s*[:.,;|–-]?\s*$", re.IGNORECASE)
ORG_NUM = re.compile(r"(?<!\d)(\d{3})[ . ]?(\d{3})[ . ]?(\d{3})(?!\d)")
ORG_LABEL = re.compile(r"(org\.?\s?(nr|nummer|no)\b|organisasjonsnummer|organisation number|organization number|"
                       r"foretaksregisteret|\bnorway\s*(reg|no)|\bNO\b)", re.IGNORECASE)


@dataclass(frozen=True)
class CompanyIdentity:
    org: str
    name: str
    street: str | None = None
    postcode: str | None = None
    city: str | None = None
    municipality: str | None = None
    phone: str | None = None


@dataclass
class IdentityResult:
    score: float
    signals: list[str] = field(default_factory=list)
    snippet: str | None = None  # literal text from the page that proves the identity signal
    veto: str | None = None
    foreign_org: str | None = None

    @property
    def publishable(self) -> bool:
        return self.score >= PUBLISH_THRESHOLD and self.veto is None


# Words too common to identify a business on their own (a page about "Nordvik Eiendom" must not match "Eiendom").
GENERIC_TOKENS = {
    "eiendom", "eiendommer", "eiendomsutvikling", "holding", "invest", "investering", "group", "gruppen", "norge",
    "norway", "norsk", "nordic", "service", "services", "bygg", "entreprenor", "consulting", "consult", "solutions",
    "partner", "partners", "drift", "utvikling", "forvaltning", "handel", "kapital", "management", "teknikk", "industri",
    "industries", "industrier", "systems", "system", "media", "design", "transport", "restaurant", "butikk", "senter",
    "center", "international", "sikkerhet", "bolig", "boliger", "utleie", "salg", "tjenester", "produkter", "norden",
    "scandinavia", "scandinavian", "oslo", "bergen", "trondheim", "stavanger", "kristiansand", "tromso",
}


def street_variants(street: str | None) -> list[str]:
    """Folded street strings to look for: the whole string and its last comma part ('c/o X, Gate 9' -> 'gate 9').
    Every variant must still end in a house number, so a bare street name never matches."""
    if not street:
        return []
    out = []
    for cand in [street, *[p.strip() for p in street.split(",")][-1:]]:
        f = fold(cand)
        if f and re.search(r"\d", f) and f not in out:
            out.append(f)
    return out


def _street_on_page(folded: str, street: str | None) -> bool:
    return any(re.search(rf"(?<![a-z0-9]){re.escape(v)}(?![a-z0-9])", folded) for v in street_variants(street))


def distinctive_tokens(name: str) -> list[str]:
    return [t for t in core_tokens(name) if len(t) >= 5 and t not in GENERIC_TOKENS and not t.isdigit()]


def core_tokens(name: str) -> list[str]:
    return [t for t in fold(name).split() if t not in LEGAL_FORMS]


def _context(text: str, start: int, end: int, pad: int = 60) -> str:
    return text[max(0, start - pad): end + pad].replace("\n", " ").strip()


def _find_literal(haystack: str, needle: str) -> tuple[int, int] | None:
    """Case-insensitive literal location of `needle` in the original text (so the snippet is verbatim)."""
    i = haystack.casefold().find(needle.casefold())
    return (i, i + len(needle)) if i >= 0 else None


def assess(ident: CompanyIdentity, pages: list[PageText]) -> IdentityResult:
    text = "\n".join(p.corpus for p in pages)
    folded = fold(text)
    low = text.casefold()
    if any(m in low for m in PARKED):
        return IdentityResult(0.1, veto="parked or for-sale domain")

    ours, foreign, others = None, None, set()
    for m in ORG_NUM.finditer(text):
        digits = "".join(m.groups())
        if not valid_orgnr(digits):
            continue
        if digits == ident.org:
            ours = ours or m
        else:
            before = text[max(0, m.start() - 30): m.start()]
            labelled = bool(ORG_LABEL.search(before))
            if labelled or ENTITY_BEFORE.search(before):  # an entity listing, not a stray number that happens to pass mod-11
                others.add(digits)
            if labelled:
                foreign = foreign or digits
    if ours and len(others) >= GROUP_LIST_LIMIT:
        # a page that lists this number among several others is a group / portfolio / manager page, not the entity's own site
        return IdentityResult(0.1, veto=f"page lists {len(others)} other organisation numbers (group or portfolio site)",
                              foreign_org=min(others))
    if ours:
        core = " ".join(core_tokens(ident.name))
        if core and not re.search(rf"(?<![a-z0-9]){re.escape(core)}(?![a-z0-9])", folded):
            # the number matches but the register's name appears nowhere (renamed, or the site pairs the number with another
            # company's name): still publishable, but not "certain", and the method string says so
            return IdentityResult(0.95, ["organisation_number", "legal_name_not_on_page"], _context(text, ours.start(), ours.end()))
        return IdentityResult(1.0, ["organisation_number"], _context(text, ours.start(), ours.end()))
    if foreign:
        return IdentityResult(0.1, veto=f"page states a different organisation number ({foreign})", foreign_org=foreign)

    core = " ".join(core_tokens(ident.name))
    if not core or not re.search(rf"(?<![a-z0-9]){re.escape(core)}(?![a-z0-9])", folded):
        # Trade name differs from the legal name: accept ONLY with a distinctive name word AND the exact street address
        # (with house number) AND postcode+city on the page (weakest publishable tier, exactly 0.90).
        dist = distinctive_tokens(ident.name)
        hit = [t for t in dist if re.search(rf"(?<![a-z0-9]){re.escape(t)}(?![a-z0-9])", folded)]
        if dist and len(hit) * 2 >= len(dist) and ident.postcode and ident.city and _street_on_page(folded, ident.street) \
                and re.search(rf"(?<!\d){ident.postcode}\s+{re.escape(fold(ident.city))}(?![a-z0-9])", folded):
            loc = _find_literal(text, (ident.street or "").split(",")[-1].strip())
            return IdentityResult(0.90, ["legal_name_partial", "street_address", "postcode_city"],
                                  _context(text, *loc) if loc else None)
        return IdentityResult(0.0, [], veto="legal name not found on page")
    signals = ["legal_name"]
    name_loc = _find_literal(text, ident.name) or _find_literal(text, " ".join(ident.name.split()[:-1]) or ident.name)

    def snippet_for(needle: str) -> str | None:
        loc = _find_literal(text, needle)
        return _context(text, *loc) if loc else None

    if ident.street and _street_on_page(folded, ident.street):
        signals.append("street_address")
        snip = snippet_for(ident.street.split(",")[-1].strip()) or snippet_for(ident.street) \
            or (name_loc and _context(text, *name_loc))
        return IdentityResult(0.95, signals, snip)
    if ident.postcode and ident.city:
        city = fold(ident.city)
        if re.search(rf"(?<!\d){ident.postcode}\s+{re.escape(city)}(?![a-z0-9])", folded):
            signals.append("postcode_city")
            loc = re.search(rf"{ident.postcode}\s+{re.escape(ident.city)}", text, re.IGNORECASE)
            return IdentityResult(0.92, signals, _context(text, loc.start(), loc.end()) if loc else None)
    if ident.phone:
        digits = re.sub(r"\D", "", ident.phone)[-8:]
        if len(digits) == 8 and digits in re.sub(r"[^0-9]", "", text):
            signals.append("registered_phone")
            return IdentityResult(0.92, signals, name_loc and _context(text, *name_loc))
    place = fold(ident.municipality or ident.city or "")
    if place and re.search(rf"(?<![a-z0-9]){re.escape(place)}(?![a-z0-9])", folded):
        signals.append("municipality_only")
        return IdentityResult(0.70, signals, name_loc and _context(text, *name_loc))
    return IdentityResult(0.50, signals, name_loc and _context(text, *name_loc))
