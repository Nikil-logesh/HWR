"""Phase 3 gate on REAL recorded Brreg responses (recorded 2026-10-03 with scripts/record_fixtures.py;
birth dates scrubbed). Invariants are checked against the raw JSON, so a wrong field mapping fails here."""
import json
from pathlib import Path

import httpx
import pytest

from signalpost.accounts import FIELDS, _dig
from signalpost.httpcache import ApiClient
from signalpost.models import Envelope
from signalpost.pipeline import register_envelope

REC = sorted((Path(__file__).parent / "fixtures" / "recorded").glob("*.json"))


def replay(path):
    rec = json.loads(path.read_text(encoding="utf-8"))
    routes = {httpx.URL(r["url"]).path: r for r in rec["responses"].values()}

    def handler(req):
        r = routes[req.url.path]
        return httpx.Response(200, json=r["body"]) if r["status"] == 200 else httpx.Response(r["status"])
    env = register_envelope(rec["org"], ApiClient(transport=httpx.MockTransport(handler)), run_id="t")
    return rec, env


def test_at_least_ten_recorded_companies_and_no_personal_dates():
    assert len(REC) >= 10
    assert all("fodselsdato" not in p.read_text(encoding="utf-8") for p in REC)
    assert all(json.loads(p.read_text())["synthetic"] is False for p in REC)


@pytest.mark.parametrize("path", REC, ids=lambda p: p.stem)
def test_recorded_company_envelope_is_valid_and_traceable(path):
    rec, env = replay(path)
    Envelope.model_validate_json(env.to_json_line())
    assert env.run.terminal_status == "completed" and env.operations.requests == 5
    c = {x.field: x for x in env.claims}
    entity = rec["responses"]["entity"]["body"]
    assert c["legal_name"].value == entity["navn"]
    assert c["legal_form"].value["code"] == entity["organisasjonsform"]["kode"]
    assert c["registered_address"].value["municipality_number"] == entity["forretningsadresse"]["kommunenummer"]
    assert c["status"].value == "active"
    assert c["roles"].availability in ("available", "not_available")
    assert "financials.total_assets" in c


@pytest.mark.parametrize("path", REC, ids=lambda p: p.stem)
def test_every_financial_value_equals_the_raw_filing_number(path):
    rec, env = replay(path)
    records = rec["responses"]["accounts"]["body"]
    for claim in env.claims:
        if not claim.field.startswith(("financials.", "financials_consolidated.")):
            continue
        prefix, name = claim.field.split(".")
        kind = "KONSERN" if prefix.endswith("consolidated") else "SELSKAP"
        end = claim.reporting_period.split("/")[1]
        match = [r for r in records if r["regnskapstype"] == kind and r["regnskapsperiode"]["tilDato"] == end]
        assert len(match) == 1
        assert claim.value["amount"] == _dig(match[0], FIELDS[name])
        # latest period only
        assert end == max(r["regnskapsperiode"]["tilDato"] for r in records if r["regnskapstype"] == kind)
        assert claim.value["currency"] == match[0]["valuta"]


@pytest.mark.parametrize("path", REC, ids=lambda p: p.stem)
def test_no_zero_invented_for_missing_financial_fields(path):
    rec, env = replay(path)
    fields = {c.field for c in env.claims}
    for kind, prefix in (("SELSKAP", "financials"), ("KONSERN", "financials_consolidated")):
        recs = sorted((r for r in rec["responses"]["accounts"]["body"] if r["regnskapstype"] == kind),
                      key=lambda r: r["regnskapsperiode"]["tilDato"])
        if not recs:
            continue
        for name, p in FIELDS.items():
            if not isinstance(_dig(recs[-1], p), (int, float)):
                assert f"{prefix}.{name}" not in fields


def test_equinor_known_values_and_group_history():
    _, env = replay(next(p for p in REC if p.stem == "923609016"))
    c = {x.field: x for x in env.claims}
    assert c["legal_name"].value == "EQUINOR ASA" and c["financials_consolidated.revenue"].value["currency"] == "USD"
    assert c["financials_consolidated.revenue"].reporting_period == "2025-01-01/2025-12-31"
    assert [h["reporting_period"].split("/")[1][:4] for h in c["financials_consolidated_history"].value] == ["2025", "2024", "2023"]
    assert c["in_group"].value is True and any(n["name"] == "STATOIL ASA" for n in c["previous_names"].value)
