"""Phase 5 gate: previous profiles stored, diffed against fresh data, typed material changes, idempotent reruns."""
import copy
import json

import httpx

from signalpost.budget import Budget
from signalpost.httpcache import ApiClient
from signalpost.pipeline import register_envelope
from signalpost.refresh import apply_refresh
from signalpost.store import SnapshotStore
from signalpost.web.fetch import WebFetcher
from signalpost.web.llm import LlmClient, Provider
from test_register_layer import load, transport_for

T1, T2, T3 = "2026-10-01T06:00:00Z", "2026-10-02T06:00:00Z", "2026-10-03T06:00:00Z"
NAME = "active_as_with_website"


def refresh(fx, store, now, run_id="r", **kw):
    client = ApiClient(transport=transport_for(fx), sleeper=lambda s: None)
    return register_envelope(fx["org"], client, run_id=run_id, store=store, now=now, **kw)


def by_field(env):
    return {c.field: c for c in env.claims}


def fx_variant(**changes):
    fx = copy.deepcopy(load(NAME))
    for k, v in changes.items():
        if k == "entity" and isinstance(v, dict):
            fx["entity"].update(v)
        else:
            fx[k] = v
    return fx


# ---------- changed address ----------
def test_address_change_is_flagged_material_with_old_new_and_sources():
    store = SnapshotStore()
    refresh(load(NAME), store, T1, "r1")
    new_addr = {"adresse": ["Nygata 9"], "postnummer": "0160", "poststed": "OSLO", "kommune": "OSLO",
                "kommunenummer": "0301", "land": "Norge"}
    env = refresh(fx_variant(entity={"forretningsadresse": new_addr}), store, T2, "r2")
    [ch] = [c for c in env.changes if c["field"] == "registered_address"]
    assert ch["change_type"] == "address_change" and ch["material"] is True
    assert ch["old_value"]["street"] == "Testveien 1" and ch["new_value"]["street"] == "Nygata 9"
    assert ch["detected_at"] == T2 and ch["previous_run_id"] == "r1"
    assert ch["source_url"].startswith("https://data.brreg.no/") and ch["source_class"] == "official_registry_live"
    assert ch["old_content_sha256"] and ch["new_content_sha256"] and ch["old_content_sha256"] != ch["new_content_sha256"]
    assert {c["field"] for c in env.changes} == {"registered_address"}  # nothing else flagged
    assert by_field(env)["registered_address"].first_observed_at == T2


# ---------- status change to bankrupt ----------
def test_status_change_to_bankrupt_is_material():
    store = SnapshotStore()
    refresh(load(NAME), store, T1, "r1")
    env = refresh(fx_variant(entity={"konkurs": True, "konkursdato": "2026-10-02"}), store, T2, "r2")
    [ch] = [c for c in env.changes if c["field"] == "status"]
    assert (ch["old_value"], ch["new_value"], ch["change_type"], ch["material"]) == ("active", "bankrupt",
                                                                                      "status_change", True)
    assert by_field(env)["status"].value == "bankrupt"


def test_name_change_flagged_and_history_recorded():
    store = SnapshotStore()
    refresh(load(NAME), store, T1, "r1")
    env = refresh(fx_variant(entity={"navn": "SYNTETISK NYTT NAVN AS",
                                     "historiskeNavn": [{"navn": "SYNTETISK TESTSELSKAP AS", "fraDato": "2015-02-20",
                                                         "tilDato": "2026-10-01"}]}), store, T2, "r2")
    ch = next(c for c in env.changes if c["field"] == "legal_name")
    assert ch["change_type"] == "name_change" and ch["material"] and ch["new_value"] == "SYNTETISK NYTT NAVN AS"


# ---------- unchanged company ----------
def test_unchanged_company_has_no_changes_keeps_first_observed_and_is_idempotent():
    store = SnapshotStore()
    e1 = refresh(load(NAME), store, T1, "r1")
    e2 = refresh(load(NAME), store, T2, "r2")
    e3 = refresh(load(NAME), store, T3, "r3")
    assert e1.changes == [] and e2.changes == [] and e3.changes == []
    c1, c3 = by_field(e1), by_field(e3)
    assert set(c1) == set(c3)
    for f in c1:
        assert c3[f].value == c1[f].value
        assert c3[f].first_observed_at == T1  # first seen on run 1, never reset
        assert c3[f].last_checked_at == T3  # check date refreshed
    assert len(store.history(load(NAME)["org"])) == 1  # identical state => no duplicate snapshot rows


def test_changed_state_adds_snapshot_and_prior_is_preserved():
    store = SnapshotStore()
    org = load(NAME)["org"]
    refresh(load(NAME), store, T1, "r1")
    refresh(fx_variant(entity={"konkurs": True}), store, T2, "r2")
    hist = store.history(org)
    assert len(hist) == 2 and by_field(hist[0])["status"].value == "active" and by_field(hist[1])["status"].value == "bankrupt"


def test_new_filing_period_detected():
    store = SnapshotStore()
    refresh(load(NAME), store, T1, "r1")
    acct = copy.deepcopy(load(NAME)["accounts"][0])
    acct["regnskapsperiode"] = {"fraDato": "2026-01-01", "tilDato": "2026-12-31"}
    acct["resultatregnskapResultat"]["driftsresultat"]["driftsinntekter"]["sumDriftsinntekter"] = 14000000
    env = refresh(fx_variant(accounts=[acct, *load(NAME)["accounts"]]), store, T2, "r2")
    ch = next(c for c in env.changes if c["field"] == "financials.revenue")
    assert ch["change_type"] == "new_filing" and ch["material"]
    assert (ch["old_reporting_period"], ch["new_reporting_period"]) == ("2025-01-01/2025-12-31", "2026-01-01/2026-12-31")
    assert ch["old_value"]["amount"] == 12500000 and ch["new_value"]["amount"] == 14000000


def test_restated_same_period_is_not_called_a_new_filing():
    store = SnapshotStore()
    refresh(load(NAME), store, T1, "r1")
    acct = copy.deepcopy(load(NAME)["accounts"])
    acct[0]["resultatregnskapResultat"]["aarsresultat"] = 650000
    env = refresh(fx_variant(accounts=acct), store, T2, "r2")
    ch = next(c for c in env.changes if c["field"] == "financials.annual_result")
    assert ch["change_type"] == "financials_restated" and {c["field"] for c in env.changes} == {"financials.annual_result"}


def test_role_change_lists_added_and_removed():
    store = SnapshotStore()
    refresh(load(NAME), store, T1, "r1")
    roles = copy.deepcopy(load(NAME)["roles"])
    roles["rollegrupper"][0]["roller"][1]["person"]["navn"] = {"fornavn": "Nina", "etternavn": "Dahl"}
    env = refresh(fx_variant(roles=roles), store, T2, "r2")
    ch = next(c for c in env.changes if c["field"] == "roles")
    assert ch["change_type"] == "role_change" and ch["material"]
    assert [r["name"] for r in ch["detail"]["added"]] == ["Nina Dahl"]
    assert [r["name"] for r in ch["detail"]["removed"]] == ["Ola Hansen"]


# ---------- failed refresh keeps last supported value ----------
def test_failed_source_carries_value_forward_and_exposes_failure():
    store = SnapshotStore()
    refresh(load(NAME), store, T1, "r1")
    fx = load(NAME)
    client = ApiClient(transport=httpx.MockTransport(
        lambda r: httpx.Response(503) if r.url.path.endswith("/roller") else transport_for(fx).handle_request(r)),
        sleeper=lambda s: None)
    env = register_envelope(fx["org"], client, run_id="r2", store=store, now=T2)
    roles = by_field(env)["roles"]
    assert roles.availability == "available" and roles.carried_forward and "retained" in roles.note
    assert roles.first_observed_at == T1 and roles.last_checked_at == T1  # NOT refreshed: it was not re-checked
    assert env.changes == []
    assert any(e.get("kind") == "carried_forward" and e["field"] == "roles" for e in env.errors)
    assert all(e.id for e in env.evidence) and set(roles.evidence_ids) <= {e.id for e in env.evidence}
    json.loads(env.to_json_line())


def test_entity_deleted_is_a_material_registry_change():
    store = SnapshotStore()
    refresh(load(NAME), store, T1, "r1")
    fx = fx_variant(entity=410, accounts=404, roles=404, subunits=404, years=404)
    env = refresh(fx, store, T2, "r2")
    ch = next(c for c in env.changes if c["field"] == "registry_record")
    assert ch["change_type"] == "registry_record_change" and ch["material"] and ch["old_value"] == "SYNTETISK TESTSELSKAP AS"
    assert by_field(env)["registry_record"].availability == "not_available"


def test_first_run_has_no_changes_and_pure_refresh_without_previous():
    fx = load(NAME)
    env = register_envelope(fx["org"], ApiClient(transport=transport_for(fx)), run_id="r1")
    out = apply_refresh(None, env, T1)
    assert out.changes == [] and all(c.first_observed_at == T1 for c in out.claims)


# ---------- website: skip unchanged sources cheaply ----------
ORG = load(NAME)["org"]
PAGE = ("<html><head><title>Testselskap</title><meta name=\"description\" content=\"Syntetisk Testselskap utvikler "
        "programvare for norske virksomheter.\"></head><body><h1>SYNTETISK TESTSELSKAP AS</h1>"
        "<p>Vi lager skreddersydd programvare.</p><footer>Testveien 1, 0150 Oslo. Org.nr " + "910 000 012" + "</footer></body></html>")


def web_stack(page):
    hits = []

    def handler(req):
        hits.append(req.url.path)
        if req.url.path == "/robots.txt":
            return httpx.Response(404)
        return httpx.Response(200, text=page[0], headers={"content-type": "text/html"})
    f = WebFetcher(Budget(500, 50), transport=httpx.MockTransport(handler), sleeper=lambda s: None,
                   resolver=lambda *a, **k: [(2, 1, 6, "", ("93.184.216.34", 0))])
    payload = {"description": None, "services": [{"page": 1, "value": "skreddersydd programvare",
                                                    "evidence_snippet": "Vi lager skreddersydd programvare."}]}
    llm = LlmClient([Provider("p", "https://llm.example/v1", "m", "k")], Budget(500, 50),
                    transport=httpx.MockTransport(lambda r: httpx.Response(200, json={
                        "choices": [{"message": {"content": json.dumps(payload)}}], "usage": {}})))
    return f, llm, hits


def test_unchanged_homepage_skips_llm_and_reuses_verified_claims():
    store, page = SnapshotStore(), [PAGE]
    f, llm, hits = web_stack(page)
    e1 = refresh(load(NAME), store, T1, "r1", fetcher=f, llm=llm)
    assert by_field(e1)["official_website"].availability == "available" and llm.usage.requests == 1
    assert by_field(e1)["products_services"].value == ["skreddersydd programvare"]
    hits.clear()
    e2 = refresh(load(NAME), store, T2, "r2", fetcher=f, llm=llm)
    assert llm.usage.requests == 1  # no new LLM call: source unchanged
    assert e2.changes == [] and by_field(e2)["products_services"].value == ["skreddersydd programvare"]
    assert by_field(e2)["official_website"].first_observed_at == T1
    assert hits == ["/"]  # homepage re-checked once (robots.txt cached per host), no secondary pages, no LLM


def test_changed_homepage_triggers_reextraction_and_change_event():
    store, page = SnapshotStore(), [PAGE]
    f, llm, _ = web_stack(page)
    refresh(load(NAME), store, T1, "r1", fetcher=f, llm=llm)
    page[0] = PAGE.replace("programvare for norske virksomheter", "skytjenester for norske virksomheter")
    e2 = refresh(load(NAME), store, T2, "r2", fetcher=f, llm=llm)
    assert llm.usage.requests == 2
    ch = next(c for c in e2.changes if c["field"] == "website_description")
    assert "skytjenester" in ch["new_value"] and "programvare" in ch["old_value"]


# ---------- cross-check against the kit's own refresh fixture ----------
def test_kit_refresh_fixture_has_exactly_the_expected_changes_and_idempotent_rerun():
    kit = json.loads((__import__("pathlib").Path(__file__).parents[1] / "kit/tests/fixtures/refresh-snapshots.json").read_text())
    org = kit["profiles"][0]["organisation_number"]

    def client(which):
        resp = kit["snapshots"][which]["responses"]
        routes = {httpx.URL(u).path: r for u, r in resp.items()}

        def h(req):
            r = routes.get(req.url.path)
            return httpx.Response(200, json=r["body"]) if r else httpx.Response(404)
        return ApiClient(transport=httpx.MockTransport(h), sleeper=lambda s: None)
    store = SnapshotStore()
    mods = ("financials", "entity")
    register_envelope(org, client("old"), run_id="old", store=store, now=T1, modules=mods)
    new = register_envelope(org, client("new"), run_id="new", store=store, now=T2, modules=mods)
    assert {c["field"] for c in new.changes} == {"employees", "financials.revenue", "financials.operating_result",
                                                  "financials.annual_result", "financials.total_assets",
                                                  "financials.equity", "financials.total_debt"}
    assert all(c["source_url"] and c["detected_at"] == T2 and c["old_content_sha256"] for c in new.changes)
    again = register_envelope(org, client("new"), run_id="new2", store=store, now=T3, modules=mods)
    assert again.changes == [] and len(store.history(org)) == 2
