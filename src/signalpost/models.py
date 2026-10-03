"""Pydantic v2 models for the terminal envelope (kit/OUTPUT_CONTRACT.md) with deterministic JSON output.

Additions beyond the minimal contract are optional: `schema_version`, claim `reporting_period`/`as_of`,
evidence `extraction_method`. Each is documented in DATA_SCHEMA.md.
"""
from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA_VERSION = "signalpost-envelope/1"
Availability = Literal["available", "not_available", "blocked", "not_applicable", "ambiguous", "failed"]
TerminalStatus = Literal["completed", "partial", "failed"]


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    source_url: str
    source_class: str
    retrieved_at: str
    content_sha256: str | None = None
    claim_span: str | None = None
    extraction_method: str | None = None


class Claim(BaseModel):
    model_config = ConfigDict(extra="forbid")
    field: str
    value: Any = None
    availability: Availability
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_ids: list[str] = Field(default_factory=list)
    reporting_period: str | None = None
    as_of: str | None = None
    note: str | None = None
    first_observed_at: str | None = None  # when this exact value was first seen (preserved across refreshes)
    last_checked_at: str | None = None  # last run that re-checked it (refreshed even when unchanged)
    carried_forward: bool = False  # refresh of this source failed; last supported value retained

    @model_validator(mode="after")
    def _rules(self) -> Claim:
        if self.availability == "available":
            if self.value is None:
                raise ValueError(f"{self.field}: available claim needs a value (missing is never zero)")
            if not self.evidence_ids:
                raise ValueError(f"{self.field}: available claim needs evidence (no evidence, no publication)")
        return self


class Run(BaseModel):
    model_config = ConfigDict(extra="forbid")
    run_id: str
    started_at: str
    completed_at: str
    terminal_status: TerminalStatus


class Operations(BaseModel):
    model_config = ConfigDict(extra="forbid")
    requests: int = 0
    runtime_ms: int = 0
    third_party_cost_usd: float = 0


class Envelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: str = SCHEMA_VERSION
    organisation_number: str
    run: Run
    claims: list[Claim] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    changes: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)
    operations: Operations = Field(default_factory=Operations)
    explanation: str | None = None

    @model_validator(mode="after")
    def _evidence_refs(self) -> Envelope:
        ids = {e.id for e in self.evidence}
        if len(ids) != len(self.evidence):
            raise ValueError("duplicate evidence ids")
        for claim in self.claims:
            missing = [i for i in claim.evidence_ids if i not in ids]
            if missing:
                raise ValueError(f"{claim.field}: unknown evidence ids {missing}")
        return self

    def to_json_line(self) -> str:
        """Deterministic: stable key order, compact separators, UTF-8."""
        return json.dumps(self.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
