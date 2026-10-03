"""Phase 3 gate: register + accounts layer against 10 SYNTHETIC Brreg-shaped fixtures (not live recordings)."""
import json
from pathlib import Path

import httpx
import pytest

from signalpost.budget import Budget
from signalpost.httpcache import ApiClient
from signalpost.models import Envelope
from signalpost.pipeline import register_envelope

FIX = Path(__file__).parent / "fixtures" / "synthetic"
NAMES = sorted(p.stem for p in FIX.glob("*.json"))


def load(name):
    return json.loads((FIX / f"{name}.json").read_text(encoding="utf-8"))


def transport_for(fx, hits=None):
    org = fx["org"]
    routes = {
        f"/enhetsregisteret/api/enheter/{org}": fx["entity"],
        f"/enhetsregisteret/api/enheter/{org}/roller": fx["roles"],
        "/enhetsregisteret/api/underenheter": fx["subunits"],
        f"/regnskapsregisteret/regnskap/{org}": fx["accounts"],
        f"/regnskapsregisteret/regnskap/aarsregnskap/kopi/{org}/aar": fx["years"],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if hits is not None:
            hits.append(str(request.url))
        body = routes[request.url.path]
        if isinstance(body, int):
            return httpx.Response(body)
        return httpx.Response(200, json=body, headers={"etag": '"v1"'})
    return httpx.MockTransport(handler)


def run(name, **kw):
    fx = load(name)
    client = ApiClient(transport=transport_for(fx), sleeper=lambda s: None, **kw)
    return fx, register_envelope(fx["org"], client, run_id="t")


def claims(env):
    return {c.field: c for c in env.claims}


def test_ten_or_more_fixtures():
    assert len(NAMES) >= 10 and all(load(n)["synthetic"] for n in NAMES)


@pytest.mark.parametrize("name", NAMES)
def test_every_fixture_yields_valid_envelope_with_evidence(name):
    fx, env = run(name)
    assert env.organisation_number == fx["org"] and env.run.terminal_status == "completed"
    Envelope.model_validate_json(env.to_json_line())
    for c in env.claims:
        if c.availability == "available":
            assert c.evidence_ids and c.value is not None
    for e in env.evidence:
        assert e.source_url.startswith("https://") and e.retrieved_at.endswith("Z")


def test_full_company_extracts_register_fields_and_roles():
    _, env = run("active_as_with_website")
    c = claims(env)
    assert c["legal_name"].value == "SYNTETISK TESTSELSKAP AS"
    assert c["legal_form"].value["code"] == "AS" and c["status"].value == "active"
    assert c["nace"].value["code"] == "62.010" and c["employees"].value == 12
    assert c["registered_address"].value["city"] == "OSLO" and c["founded"].value == "2015-02-20"
    assert c["registry_website"].value == "www.syntetisk-test.example"
    names = {(r["role"], r["name"]) for r in c["roles"].value}
    assert ("Styrets leder", "Kari Nordmann") in names and ("Daglig leder", "Kari Nordmann") in names
    assert "fodselsdato" not in json.dumps(c["roles"].value)  # birth dates never read
    assert c["workplaces"].value[0]["address"]["city"] == "BERGEN"
    assert c["financial_history_years"].value == ["2024", "2025"]


def test_financials_have_period_and_exact_numbers():
    _, env = run("active_as_with_website")
    c = claims(env)
    rev = c["financials.revenue"]
    assert rev.value == {"amount": 12500000, "currency": "NOK"}
    assert rev.reporting_period == "2025-01-01/2025-12-31" and rev.as_of == "2025-12-31"
    ev = next(e for e in env.evidence if e.id == rev.evidence_ids[0])
    assert "12500000" in ev.claim_span and ev.content_sha256 and ev.source_class == "official_annual_accounts"


def test_zero_preserved_and_missing_never_zero():
    _, env = run("zero_revenue_missing_field")
    c = claims(env)
    assert c["financials.revenue"].value["amount"] == 0 and c["financials.revenue"].availability == "available"
    assert "financials.profit_before_tax" not in c  # missing is omitted, not 0
    assert c["employees"].value == 0


def test_no_accounts_is_not_available_not_zero():
    _, env = run("enk_no_accounts")
    c = claims(env)
    assert c["financials"].availability == "not_available" and c["financials"].value is None
    assert c["roles"].availability == "not_available" and c["workplaces"].availability == "not_available"
    assert not any(k.startswith("financials.") for k in c)


@pytest.mark.parametrize("name,status", [("bankrupt_as", "bankrupt"), ("liquidating_as", "liquidating"),
                                         ("nuf_branch", "active")])
def test_status_detection(name, status):
    _, env = run(name)
    assert claims(env)["status"].value == status


def test_consolidated_kept_separate_from_company_accounts():
    _, env = run("large_asa_consolidated")
    c = claims(env)
    assert c["financials_consolidated.revenue"].value["amount"] == 9800000000
    assert c["financials.revenue"].value["amount"] == 12000000


def test_employee_count_not_registered_is_explicit():
    _, env = run("foundation_no_employee_count")
    assert claims(env)["employees"].availability == "not_available"


def test_deleted_entity_410_falls_back_to_universe_row():
    fx = load("deleted_entity_410")
    client = ApiClient(transport=transport_for(fx), sleeper=lambda s: None)
    row = {"name": "SYNTETISK SLETTET AS", "legal_form": "AS", "bankrupt": False, "liquidating": False,
           "industry_code": "00.000", "municipality": "OSLO", "municipality_number": "0301", "employees": None,
           "website": "", "latest_submitted_accounts": "2025"}
    env = register_envelope(fx["org"], client, run_id="t", universe_row=row)
    c = claims(env)
    assert c["registry_record"].availability == "not_available"
    assert c["legal_name"].value == "SYNTETISK SLETTET AS"
    assert "nace" not in c and "employees" not in c  # 00.000 / None are not invented as facts


def test_wrong_org_in_response_is_ambiguous_not_published():
    fx = load("active_as_with_website")
    fx["entity"]["organisasjonsnummer"] = "999999999"
    client = ApiClient(transport=transport_for(fx), sleeper=lambda s: None)
    env = register_envelope(fx["org"], client, run_id="t")
    c = claims(env)
    assert c["registry_record"].availability == "ambiguous" and "legal_name" not in c


def test_deterministic_json():
    a = run("active_as_with_website")[1].model_dump(mode="json")
    b = run("active_as_with_website")[1].model_dump(mode="json")
    for env in (a, b):
        env["run"] = env["operations"] = None
        for e in env["evidence"]:
            e["retrieved_at"] = None
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_etag_revalidation_reuses_cache_and_counts_request():
    fx = load("active_as_with_website")
    hits = []

    def handler(request):
        hits.append(request.headers.get("if-none-match"))
        if request.headers.get("if-none-match") == '"v1"':
            return httpx.Response(304)
        return httpx.Response(200, json=fx["entity"], headers={"etag": '"v1"'})
    budget = Budget(10, 10)
    client = ApiClient(transport=httpx.MockTransport(handler), budget=budget)
    url = f"https://data.brreg.no/enhetsregisteret/api/enheter/{fx['org']}"
    a, b = client.get_json(url, fx["org"]), client.get_json(url, fx["org"])
    assert a.body == b.body and b.from_cache and hits == [None, '"v1"'] and budget.used == 2


def test_retry_429_then_success_and_budget_exhaustion():
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        return httpx.Response(429, headers={"retry-after": "0"}) if calls["n"] < 3 else httpx.Response(200, json={})
    c = ApiClient(transport=httpx.MockTransport(handler), sleeper=lambda s: None)
    assert c.get_json("https://x/a", "o").ok and calls["n"] == 3
    tight = ApiClient(transport=httpx.MockTransport(lambda r: httpx.Response(500)), budget=Budget(2, 2),
                      sleeper=lambda s: None)
    r = tight.get_json("https://x/a", "o")
    assert r.status == -1 and r.error == "budget_exhausted"


def test_exhausted_budget_yields_failed_claims_not_missing_envelope():
    fx = load("active_as_with_website")
    client = ApiClient(transport=transport_for(fx), budget=Budget(2, 2), sleeper=lambda s: None)
    env = register_envelope(fx["org"], client, run_id="t")
    assert env.run.terminal_status == "partial" and env.operations.requests == 2
    assert "financials.revenue" in claims(env)  # the two requests that fit the budget went to the highest-value modules
    assert claims(env)["roles"].availability == "failed"


def test_unavailable_claims_never_carry_values():
    for name in NAMES:
        _, env = run(name)
        for c in env.claims:
            if c.availability != "available":
                assert c.value is None
