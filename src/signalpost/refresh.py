"""Refresh as a diff: previous supported claims vs fresh claims -> stamped claims + typed changes[].

Pure function (no I/O). Rules:
  * unchanged value  -> keep first_observed_at, bump last_checked_at; NO change event (no false changes)
  * changed value    -> change event (kit schema + detected_at/change_type/material), first_observed_at = now
  * newly available  -> field_added / new_filing;  no longer available -> field_removed
  * fresh failed/blocked (transient) while a supported value existed -> value carried forward, flagged, and the
    failure is exposed in errors[] (a failed refresh never erases the last supported value)
Idempotent: refreshing with identical data yields identical claims (apart from last_checked_at) and no changes.
"""
from __future__ import annotations

import json
from typing import Any

from .claims import ClaimSet
from .models import Claim, Envelope

TRANSIENT = {"failed", "blocked"}
MATERIAL = {"status", "legal_name", "registered_address", "legal_form", "official_website", "roles",
            "registry_record"}
TYPE_BY_FIELD = {"status": "status_change", "legal_name": "name_change", "registered_address": "address_change",
                 "postal_address": "address_change", "legal_form": "legal_form_change", "roles": "role_change",
                 "official_website": "website_change", "workplaces": "workplace_change",
                 "employees": "employees_change", "registry_record": "registry_record_change"}


def _key(c: Claim) -> tuple[str, str]:
    return c.field, ""  # one live claim per field; reporting_period is part of the value comparison for filings


def _canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, ensure_ascii=False)


def _same(a: Claim, b: Claim, a_is_fallback: bool = False) -> bool:
    if a.availability != b.availability or (a.reporting_period or "") != (b.reporting_period or ""):
        return False
    if _canon(a.value) == _canon(b.value):
        return True
    # a bulk/universe-row fallback claim carries fewer keys than the live record: compare only what it states
    return bool(a_is_fallback and isinstance(a.value, dict) and isinstance(b.value, dict)
                and all(b.value.get(k) == v for k, v in a.value.items()))


def _is_fallback(env: Envelope, c: Claim) -> bool:
    ev = _ev(env, c)
    return bool(ev and ev.source_class == "official_registry_bulk")


def _ev(env: Envelope, claim: Claim | None):
    if claim and claim.evidence_ids:
        return next((e for e in env.evidence if e.id == claim.evidence_ids[0]), None)
    return None


def _detail(old: Any, new: Any) -> dict[str, Any] | None:
    if isinstance(old, list) and isinstance(new, list):
        o, n = {_canon(x) for x in old}, {_canon(x) for x in new}
        return {"added": [json.loads(x) for x in sorted(n - o)], "removed": [json.loads(x) for x in sorted(o - n)]}
    return None


def _ctype(field: str, kind: str, old: Claim | None, new: Claim | None) -> str:
    if field == "registry_record":
        return "registry_record_change"
    if field.startswith(("financials.", "financials_consolidated.")):
        if kind == "changed" and old and new and old.reporting_period != new.reporting_period:
            return "new_filing"
        return "new_filing" if kind == "added" else "financials_restated" if kind == "changed" else "field_removed"
    if kind in ("added", "removed"):
        return f"field_{kind}"
    return TYPE_BY_FIELD.get(field, "value_changed")


def apply_refresh(previous: Envelope | None, fresh: Envelope, now: str) -> Envelope:
    """Return `fresh` re-assembled with observation dates, carried-forward claims and changes[]."""
    prev = {_key(c): c for c in (previous.claims if previous else [])}
    cs = ClaimSet()
    cs.evidence = list(fresh.evidence)  # carried claims append their evidence after the fresh evidence
    out_claims: list[Claim] = []
    prev_classes = {e.source_class for e in previous.evidence} if previous else set()
    prev_has_live = bool(previous and any(not _is_fallback(previous, c) and c.availability == "available"
                                          and c.evidence_ids for c in previous.claims))
    errors = list(fresh.errors)
    changes: list[dict[str, Any]] = []
    seen = set()
    for c in fresh.claims:
        key = _key(c)
        seen.add(key)
        old = prev.get(key)
        old_ok = bool(old and old.availability == "available")
        if (previous is not None and old is None and c.availability == "available" and prev_has_live
                and _is_fallback(fresh, c)):
            continue  # free universe-row duplicate of something the live register already covered
        if (old_ok and previous is not None and old is not None and c.availability == "available"
                and _is_fallback(fresh, c) and not _is_fallback(previous, old)):
            # live register unavailable this time: the free universe-row value must not overwrite the live one
            out_claims.append(cs.carry(old, previous, carried_forward=True,
                                       note="live register unavailable this run; last live value retained"))
            continue
        if c.availability in TRANSIENT and old_ok and previous is not None and old is not None:
            kept = cs.carry(old, previous, carried_forward=True,
                            note=f"refresh failed ({c.availability}: {c.note}); last supported value retained")
            out_claims.append(kept)  # keeps the old first_observed_at / last_checked_at
            errors.append({"module": "refresh", "kind": "carried_forward", "field": c.field,
                           "reason": c.note or c.availability})
            continue
        if old and _same(old, c, previous is not None and _is_fallback(previous, old)):
            first = old.first_observed_at or (previous.run.started_at if previous else now)
            out_claims.append(c.model_copy(update={"first_observed_at": first, "last_checked_at": now}))
            continue
        out_claims.append(c.model_copy(update={"first_observed_at": now, "last_checked_at": now}))
        if previous is None:
            continue
        gone = next((o for o in previous.claims if o.field == "legal_name" and o.availability == "available"), None)
        if c.field == "registry_record" and c.availability == "not_available" and gone:
            changes.append(_change(previous, fresh, "registry_record", "removed", gone, c, now))
            continue
        kind = ("changed" if old_ok else "added") if c.availability == "available" \
            else "removed" if old_ok else None
        new_ev = _ev(fresh, c)
        if kind == "added" and new_ev is not None and new_ev.source_class not in prev_classes:
            continue  # the previous run never observed this source: a first observation, not a change
        if kind:
            changes.append(_change(previous, fresh, c.field, kind, old, c, now))
    for key, old in prev.items():  # supported earlier but absent from this run (e.g. module skipped for budget)
        if key not in seen and old.availability == "available" and previous is not None \
                and not _is_fallback(previous, old):  # stale fallback-only facts are dropped, not carried forever
            out_claims.append(cs.carry(old, previous, carried_forward=True,
                                       note="not re-checked in this run; last supported value retained"))
    out_claims.sort(key=lambda c: (c.field, c.reporting_period or ""))
    return fresh.model_copy(update={"claims": out_claims, "evidence": cs.evidence, "changes": changes,
                                    "errors": errors})


def _change(previous: Envelope, fresh: Envelope, field: str, kind: str, old: Claim | None, new: Claim | None,
            now: str) -> dict[str, Any]:
    old_ev, new_ev = _ev(previous, old), _ev(fresh, new)
    ctype = _ctype(field, kind, old, new)
    row = {
        "organisation_number": fresh.organisation_number, "field": field, "change_type": ctype,
        "material": field in MATERIAL or ctype in ("new_filing", "financials_restated", "status_change"),
        "old_value": old.value if old else None, "new_value": new.value if new else None,
        "old_reporting_period": old.reporting_period if old else None,
        "new_reporting_period": new.reporting_period if new else None,
        "detected_at": now, "previous_run_id": previous.run.run_id,
        "source_url": (new_ev or old_ev).source_url if (new_ev or old_ev) else None,
        "source_class": (new_ev or old_ev).source_class if (new_ev or old_ev) else None,
        "retrieved_at": new_ev.retrieved_at if new_ev else fresh.run.completed_at,
        "effective_at": new.as_of if new else None,
        "old_content_sha256": old_ev.content_sha256 if old_ev else None,
        "new_content_sha256": new_ev.content_sha256 if new_ev else None,
        "status": new.availability if new else "not_available",
    }
    detail = _detail(row["old_value"], row["new_value"])
    if detail:
        row["detail"] = detail
    return row
