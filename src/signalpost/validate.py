"""Validate envelopes against kit/OUTPUT_CONTRACT.md and RULES.md checks. The kit ships no scorer for this
contract (its scorers consume an older profile shape), so this is our own gate, run in benchmarks and tests."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

STATES = {"available", "not_available", "blocked", "not_applicable", "ambiguous", "failed"}
REQUIRED = ("organisation_number", "run", "claims", "evidence", "changes", "errors", "operations")
RUN_KEYS = ("run_id", "started_at", "completed_at", "terminal_status")
WEB_SPAN_FIELDS = ("website_description", "contact_email_", "contact_phone_")


def validate_envelope(d: dict[str, Any]) -> list[str]:
    org = d.get("organisation_number")
    bad: list[str] = [f"missing key {k}" for k in REQUIRED if k not in d]
    bad += [f"run.{k} missing" for k in RUN_KEYS if k not in (d.get("run") or {})]
    ev = {e.get("id"): e for e in d.get("evidence") or []}
    if len(ev) != len(d.get("evidence") or []):
        bad.append("duplicate evidence ids")
    for e in ev.values():
        for k in ("source_url", "source_class", "retrieved_at"):
            if not e.get(k):
                bad.append(f"evidence {e.get('id')} missing {k}")
    for c in d.get("claims") or []:
        f = c.get("field", "?")
        if c.get("availability") not in STATES:
            bad.append(f"{f}: illegal availability {c.get('availability')!r}")
        for i in c.get("evidence_ids") or []:
            if i not in ev:
                bad.append(f"{f}: unknown evidence id {i}")
        if c.get("availability") == "available":
            if c.get("value") is None:
                bad.append(f"{f}: available without value")
            if not c.get("evidence_ids"):
                bad.append(f"{f}: available without evidence")
            first = ev.get((c.get("evidence_ids") or [None])[0]) or {}
            if f.startswith(("financials", "financials_consolidated")) and not f.endswith("history"):
                if first.get("source_class") != "official_annual_accounts":
                    bad.append(f"{f}: financial value not from the official accounts API")
                if not c.get("reporting_period"):
                    bad.append(f"{f}: financial value without reporting period")
            if f.startswith(WEB_SPAN_FIELDS) and str(c.get("value", "")).casefold() not in \
                    str(first.get("claim_span", "")).casefold():
                bad.append(f"{f}: evidence snippet does not contain the value")
            if f in ("open_positions", "public_activity"):
                spans = " ".join((ev.get(i) or {}).get("claim_span", "") for i in c.get("evidence_ids") or []).casefold()
                for item in c.get("value") or []:
                    if str(item.get("title", "")).casefold() not in spans:
                        bad.append(f"{f}: item {str(item.get('title'))[:40]!r} not supported by its evidence snippets")
                    if f == "public_activity" and not item.get("date"):
                        bad.append(f"{f}: item without a date")
                if len(c.get("evidence_ids") or []) != len(c.get("value") or []):
                    bad.append(f"{f}: needs one evidence record per item")
        elif c.get("value") is not None:
            bad.append(f"{f}: unavailable claim carries a value")
    return [f"{org}: {b}" for b in bad]


def validate_file(path: str | Path, expected_orgs: list[str] | None = None) -> dict[str, Any]:
    lines = [ln for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip()]
    envs = [json.loads(ln) for ln in lines]
    problems = [p for e in envs for p in validate_envelope(e)]
    orgs = [e.get("organisation_number") for e in envs]
    checks = {"unique_organisation_numbers": len(orgs) == len(set(orgs))}
    if expected_orgs is not None:
        checks["exactly_one_envelope_per_input"] = orgs == expected_orgs
    return {"envelopes": len(envs), "problems": problems, "checks": checks,
            "passed": not problems and all(checks.values())}
