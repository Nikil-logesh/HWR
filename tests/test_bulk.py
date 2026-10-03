"""Bulk register snapshots: streaming parser, filtering, budget (1 request), equivalence with per-company calls."""
import gzip
import json

import httpx
import pytest

from signalpost import bulk
from signalpost.budget import Budget
from signalpost.claims import ClaimSet
from signalpost.httpcache import ApiClient
from signalpost.pipeline import register_envelope
from signalpost.planner import Company, plan_batch
from signalpost.register import roles_claims, subunit_claims
from test_register_layer import load

FX = load("active_as_with_website")
ORG = FX["org"]


def gz_array(objs, indent=2):
    return gzip.compress(json.dumps(objs, ensure_ascii=False, indent=indent).encode("utf-8"))


def chunks(data, n):
    return [data[i:i + n] for i in range(0, len(data), n)]


# ---------- streaming parser ----------
@pytest.mark.parametrize("size", [1, 3, 7, 64, 100_000])
def test_parser_is_independent_of_chunk_boundaries(size):
    objs = [{"a": 1, "s": "brace } and { inside, comma, ]"}, {"navn": "ÆØÅ æøå – ü €", "n": [1, {"x": None}]},
            {"deep": {"er": {"nested": [[], {}]}}}]
    out = list(bulk.iter_json_array_gz(chunks(gz_array(objs), size)))
    assert out == objs


def test_parser_empty_array_and_compact_format():
    assert list(bulk.iter_json_array_gz(chunks(gz_array([]), 5))) == []
    assert list(bulk.iter_json_array_gz(chunks(gz_array([{"a": 1}, {"b": 2}], indent=None), 4))) == [{"a": 1}, {"b": 2}]


def test_truncated_stream_is_detected_not_silently_accepted():
    data = gz_array([{"a": "x" * 500} for _ in range(20)])
    cut = gzip.compress(gzip.decompress(data)[:-40])  # valid gzip, JSON cut mid-object
    with pytest.raises(bulk.BulkUnavailable):
        list(bulk.iter_json_array_gz(chunks(cut, 50)))


# ---------- roles bulk ----------
def roles_record(org, fornavn="Kari"):
    return {"organisasjonsnummer": org, "rollegrupper": FX["roles"]["rollegrupper"] if org == ORG else [
        {"type": {"kode": "DAGL", "beskrivelse": "Daglig leder"}, "roller": [
            {"type": {"kode": "DAGL", "beskrivelse": "Daglig leder"}, "avregistrert": False,
             "person": {"navn": {"fornavn": fornavn, "etternavn": "Test"}, "fodselsdato": "1980-01-01"}}]}]}


def transport(data, status=200, hits=None):
    def handler(req):
        if hits is not None:
            hits.append((str(req.url), req.headers.get("accept")))
        return httpx.Response(status, content=iter(chunks(data, 4096)))  # a real stream, like the network
    return httpx.MockTransport(handler)


def test_bulk_roles_filters_wanted_counts_one_request_and_marks_absent_as_404():
    data = gz_array([roles_record(o) for o in ("910000020", ORG, "910000039")] + [roles_record("999999999")])
    b, hits = Budget(100, 15), []
    out = bulk.bulk_roles({ORG, "910000047"}, b, transport=transport(data, hits=hits))
    assert b.used == 1 and len(hits) == 1 and hits[0][0] == bulk.ROLES_BULK_URL
    assert out[ORG].ok and out[ORG].via == "bulk" and out[ORG].requests == 0
    assert out["910000047"].status == 404 and out[ORG].url.endswith(f"/enheter/{ORG}/roller")
    assert "999999999" not in out and out[ORG].sha256 and out[ORG].retrieved_at.endswith("Z")


def test_bulk_roles_claims_equal_per_company_claims_apart_from_provenance():
    per_company = ClaimSet()
    from signalpost.httpcache import Fetched
    roles_claims(per_company, ORG, Fetched("u", 200, FX["roles"], "h", "2026-10-03T00:00:00Z"))
    via_bulk = ClaimSet()
    got = bulk.bulk_roles({ORG}, Budget(5, 5), transport=transport(gz_array([roles_record(ORG)])))
    roles_claims(via_bulk, ORG, got[ORG])
    a, b = per_company.claims[0], via_bulk.claims[0]
    assert a.value == b.value and a.field == b.field == "roles"
    assert via_bulk.evidence[0].extraction_method == "brreg_roles_bulk_snapshot"
    assert via_bulk.evidence[0].source_url == f"https://data.brreg.no/enhetsregisteret/api/enheter/{ORG}/roller"
    assert "fodselsdato" not in json.dumps(b.value)


# ---------- subunits bulk ----------
def test_bulk_subunits_groups_by_parent_and_matches_per_company_shape():
    unit = FX["subunits"]["_embedded"]["underenheter"][0]
    data = gz_array([{**unit, "overordnetEnhet": ORG}, {**unit, "organisasjonsnummer": "911000013",
                                                          "overordnetEnhet": "910000020"}])
    hits = []
    out = bulk.bulk_subunits({ORG, "910000047"}, Budget(5, 5), transport=transport(data, hits=hits))
    assert hits[0][1] == bulk.SUBUNITS_ACCEPT and out["910000047"].status == 404
    cs = ClaimSet()
    subunit_claims(cs, ORG, out[ORG])
    assert cs.claims[0].availability == "available" and cs.claims[0].value[0]["address"]["city"] == "BERGEN"
    assert cs.evidence[0].extraction_method == "brreg_subunits_bulk_snapshot"
    cs2 = ClaimSet()
    subunit_claims(cs2, "910000047", out["910000047"])
    assert cs2.claims[0].availability == "not_available"


# ---------- failure modes fall back, never crash ----------
def test_http_error_and_budget_and_deadline_raise_bulk_unavailable():
    with pytest.raises(bulk.BulkUnavailable, match="HTTP 503"):
        bulk.bulk_roles({ORG}, Budget(5, 5), transport=transport(b"", 503))
    with pytest.raises(bulk.BulkUnavailable, match="budget"):
        bulk.bulk_roles({ORG}, Budget(0, 5), transport=transport(b""))
    b = Budget(5, 5)
    b.expire()
    with pytest.raises(bulk.BulkUnavailable):
        bulk.bulk_subunits({ORG}, b, transport=transport(gz_array([])))
    with pytest.raises(bulk.BulkUnavailable):  # not gzip at all
        bulk.bulk_roles({ORG}, Budget(5, 5), transport=transport(b"<html>nope</html>"))


def test_deadline_during_download_aborts():
    now = [0.0]
    b = Budget(5, 5, deadline=5.0, clock=lambda: now[0])
    data = gz_array([roles_record(f"9100000{i:02d}") for i in range(50)])

    def slow():
        for c in chunks(data, 40):
            now[0] += 1.0
            yield c

    def handler(req):
        return httpx.Response(200, content=slow())
    with pytest.raises(bulk.BulkUnavailable, match="deadline"):
        bulk.bulk_roles({ORG}, b, transport=httpx.MockTransport(handler))


# ---------- pipeline + planner integration ----------
def test_prefetched_modules_cost_zero_requests():
    got_r = bulk.bulk_roles({ORG}, Budget(5, 5), transport=transport(gz_array([roles_record(ORG)])))
    got_s = bulk.bulk_subunits({ORG}, Budget(5, 5), transport=transport(gz_array(
        [{**FX["subunits"]["_embedded"]["underenheter"][0], "overordnetEnhet": ORG}])))
    seen = []

    def handler(req):
        seen.append(req.url.path)
        return httpx.Response(200, json=FX["entity"] if req.url.path.endswith(ORG) else FX["accounts"])
    env = register_envelope(ORG, ApiClient(transport=httpx.MockTransport(handler)), run_id="t",
                            modules=("financials", "entity", "roles", "subunits"),
                            prefetched={"roles": got_r[ORG], "subunits": got_s[ORG]})
    assert env.operations.requests == 2 and len(seen) == 2 and not any("roller" in p for p in seen)
    c = {x.field: x for x in env.claims}
    assert c["roles"].availability == "available" and c["workplaces"].availability == "available"


def test_planner_counts_free_modules_as_zero_cost():
    cos = [Company(f"{i}", True, "62.010", frozenset({"roles", "subunits"})) for i in range(100)]
    plans = plan_batch(cos, 1000, 15)
    assert all({"roles", "subunits"} <= set(p.modules) for p in plans.values())
    assert all(p.est_requests == 1 + 5 for p in plans.values())  # financials + (entity + web 4)
    big = [Company(f"{i}", i % 9 == 0, "62.010", frozenset({"roles", "subunits"})) for i in range(1000)]
    from signalpost.planner import summarize
    s = summarize(plan_batch(big, 2000, 15))
    assert s["roles"] == s["subunits"] == 1000 and s["estimated_requests"] <= 2000
