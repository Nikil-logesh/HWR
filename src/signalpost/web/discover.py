"""Website discovery for companies that list no website in the register (~89% of them).

RULES.md: search/discovery generates CANDIDATES, never evidence. The only candidates built here are domain names derived
from the legal name. A candidate becomes the company's website only if the normal identity gate then proves it, with a
stricter threshold than a registered site (DISCOVERY_MIN_SCORE): the organisation number, or the full legal name plus the
exact street address. Everything else stays "not published".
"""
from __future__ import annotations

import re

from .identity import GENERIC_TOKENS, CompanyIdentity, core_tokens
from .text import fold

DISCOVERY_MIN_SCORE = 0.95
MAX_CANDIDATES = 3
# entity types whose public pages are usually a manager's or a platform's, not their own domain
SKIP_FIRST_WORDS = {"borettslag", "borettslaget", "sameie", "sameiet", "boligsameie", "boligsameiet", "boligselskap",
                    "boligselskapet", "eierseksjonssameie", "stiftelsen", "stiftelse", "legat", "legatet", "fond", "fondet"}


def _tokens(name: str) -> list[str]:
    return [re.sub(r"[^a-z0-9]", "", t) for t in core_tokens(name) if re.sub(r"[^a-z0-9]", "", t)]


def worth_trying(name: str) -> bool:
    first = fold(name).split(" ")[0] if fold(name) else ""
    toks = _tokens(name)
    return bool(toks) and first not in SKIP_FIRST_WORDS and any(len(t) >= 4 and t not in GENERIC_TOKENS for t in toks) \
        and len("".join(toks)) >= 5


def candidate_urls(name: str, limit: int = MAX_CANDIDATES) -> list[str]:
    """Homepage candidates, most likely first: name.no, name-with-hyphens.no, name.com."""
    toks = _tokens(name)
    if not toks or not worth_trying(name):
        return []
    joined, dashed = "".join(toks), "-".join(toks)
    labels = [(joined, "no")]
    if len(toks) > 1:
        labels.append((dashed, "no"))
    labels.append((joined, "com"))
    out: list[str] = []
    for label, tld in labels:
        if 3 <= len(label) <= 60 and not label.startswith("-"):
            url = f"https://{label}.{tld}/"
            if url not in out:
                out.append(url)
    return out[:limit]


def plausibly_the_company(ident: CompanyIdentity, folded_text: str) -> bool:
    """Cheap pre-filter on a candidate's homepage before spending more requests: one of the company's own name words (or
    its organisation number) appears. The identity gate decides afterwards."""
    toks = [t for t in _tokens(ident.name) if len(t) >= 4 and t not in GENERIC_TOKENS]
    if any(re.search(rf"(?<![a-z0-9]){re.escape(t)}(?![a-z0-9])", folded_text) for t in toks):
        return True
    return bool(ident.org and ident.org in re.sub(r"\D", "", folded_text))
