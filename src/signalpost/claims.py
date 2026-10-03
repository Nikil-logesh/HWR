"""Helper that assembles claims + evidence with deterministic ids and enforces evidence-for-publication."""
from __future__ import annotations

from typing import Any

from .models import Availability, Claim, Evidence


class ClaimSet:
    def __init__(self) -> None:
        self.claims: list[Claim] = []
        self.evidence: list[Evidence] = []

    def add_evidence(self, *, source_url: str, source_class: str, retrieved_at: str, sha256: str | None,
                     span: str | None, method: str) -> str:
        ev_id = f"ev-{len(self.evidence) + 1}"
        self.evidence.append(Evidence(id=ev_id, source_url=source_url, source_class=source_class,
                                      retrieved_at=retrieved_at, content_sha256=sha256, claim_span=span,
                                      extraction_method=method))
        return ev_id

    def available(self, field: str, value: Any, *, confidence: float, source_url: str, source_class: str,
                  retrieved_at: str, sha256: str | None, span: str, method: str,
                  reporting_period: str | None = None, as_of: str | None = None, note: str | None = None) -> None:
        ev = self.add_evidence(source_url=source_url, source_class=source_class, retrieved_at=retrieved_at,
                               sha256=sha256, span=span, method=method)
        self.claims.append(Claim(field=field, value=value, availability="available", confidence=confidence,
                                 evidence_ids=[ev], reporting_period=reporting_period, as_of=as_of, note=note))

    def unavailable(self, field: str, availability: Availability, *, note: str, source_url: str | None = None,
                    source_class: str | None = None, retrieved_at: str | None = None, sha256: str | None = None,
                    method: str = "http_status") -> None:
        ids: list[str] = []
        if source_url and source_class and retrieved_at:
            ids.append(self.add_evidence(source_url=source_url, source_class=source_class,
                                         retrieved_at=retrieved_at, sha256=sha256, span=note, method=method))
        self.claims.append(Claim(field=field, value=None, availability=availability, confidence=1.0 if
                                 availability in ("not_available", "not_applicable") else 0.0,
                                 evidence_ids=ids, note=note))

    def sorted_claims(self) -> list[Claim]:
        return sorted(self.claims, key=lambda c: (c.field, c.reporting_period or ""))
