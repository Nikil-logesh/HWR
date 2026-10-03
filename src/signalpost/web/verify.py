"""Literal-snippet verifier (rule 4). A web fact is publishable only if, in code:
  1. its evidence_snippet occurs literally in the fetched page corpus, AND
  2. its value occurs literally inside that snippet.
Comparison is whitespace/case-insensitive but otherwise exact (no stemming, no fuzzy match)."""
from __future__ import annotations

from dataclasses import dataclass

from .text import lit

MAX_VALUE = 600


@dataclass(frozen=True)
class Candidate:
    field: str
    value: str
    snippet: str
    page_url: str
    method: str  # e.g. "jsonld", "meta", "mailto", "llm"


def verify(c: Candidate, corpus_by_url: dict[str, str]) -> tuple[bool, str]:
    value, snippet = lit(c.value), lit(c.snippet)
    if not value or not snippet:
        return False, "empty value or snippet"
    if len(value) > MAX_VALUE:
        return False, "value too long"
    corpus = corpus_by_url.get(c.page_url)
    if corpus is None:
        return False, "snippet page was not fetched"
    if snippet not in lit(corpus):
        return False, "snippet not found in page"
    if value not in snippet:
        return False, "snippet does not contain value"
    return True, "ok"
