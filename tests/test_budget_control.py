"""Phase 7: planner, global/per-company budgets, wall-clock cutoff with safe partial output, validator."""
import json

import httpx

from signalpost.budget import Budget
from signalpost.httpcache import ApiClient
from signalpost.inputs import InputRow
from signalpost.models import Envelope
from signalpost.pipeline import placeholder_envelope, register_envelope
from signalpost.planner import Company, plan_batch, summarize
from signalpost.runner import run_planned_batch
from signalpost.validate import validate_envelope, validate_file
from test_register_layer import load, transport_for

W = (3, 2, 7, 6, 5, 4, 3, 2)


def orgs(n):
    out, i = [], 81000000
    while len(out) < n:
        i += 1
        r = 11 - sum(int(a) * b for a, b in zip(str(i), W, strict=True)) % 11
        r = 0 if r == 11 else r
        if r != 10:
            out.append(f"{i}{r}")
    return out


def companies(n, web_every=9):
    return [Company(o, has_website=(k % web_every == 0), nace="62.010") for k, o in enumerate(orgs(n))]


# ---------- planner ----------
def test_generous_budget_plans_everything_and_stays_under_cap():
    cos = companies(100)
    plans = plan_batch(cos, 2000, 15, llm=True)
    s = summarize(plans)
    assert all(set(p.modules) == {"financials", "entity", "roles", "subunits"} for p in plans.values())
    assert s["web"] == sum(c.has_website for c in cos) and s["estimated_requests"] <= 2000 * 0.92
    assert s["estimated_requests_per_company"] < 15 and all(p.est_requests <= 15 for p in plans.values())


def test_tight_budget_drops_lowest_value_tiers_first_and_never_overspends():
    cos = companies(1000)
    plans = plan_batch(cos, 2000, 15, llm=False)
    s = summarize(plans)
    assert s["estimated_requests"] <= 2000 * 0.92
    assert s["financials"] == 1000  # highest-value tier is filled first
    assert s["web"] == sum(c.has_website for c in cos)  # then the scarce web tier
    assert s["subunits"] < 1000 and s["entity"] < 1000  # lowest tiers dropped under pressure
    assert s["financials"] >= s["roles"] >= s["subunits"]


def test_zero_and_tiny_budgets():
    cos = companies(10)
    assert all(not p.modules for p in plan_batch(cos, 0).values())
    p = plan_batch(cos, 5, 15)
    assert sum(len(x.modules) for x in p.values()) <= 5


def test_web_company_always_gets_entity_record_for_the_address_signal():
    plans = plan_batch(companies(20), 2000, 15)
    for c in companies(20):
        if c.has_website:
            assert plans[c.org].web and "entity" in plans[c.org].modules


def test_per_company_cap_and_financial_sector_single_attempt():
    plans = plan_batch([Company("1", True, "64.190"), Company("2", True, "62.010")], 1000, per_company_cap=3)
    assert all(p.est_requests <= 3 for p in plans.values())
    assert plans["1"].accounts_attempts == 1 and plans["2"].accounts_attempts == 3


# ---------- budget / deadline ----------
def test_deadline_and_expire_refuse_all_further_requests():
    now = [0.0]
    b = Budget(10, 5, deadline=10.0, clock=lambda: now[0])
    assert b.take("a") and b.seconds_left() == 10.0
    now[0] = 10.0
    assert b.expired and not b.take("a") and b.used == 1
    b2 = Budget(10, 5)
    assert b2.take("a")
    b2.expire()
    assert not b2.take("a")


def test_global_and_per_company_caps():
    b = Budget(3, 2)
    assert [b.take("a"), b.take("a"), b.take("a"), b.take("b"), b.take("b")] == [True, True, False, True, False]
    assert b.used == 3 and b.remaining_total == 0


# ---------- placeholder: zero network ----------
def test_placeholder_uses_no_network_and_is_valid():
    row = {"name": "SYNTETISK TESTSELSKAP AS", "legal_form": "AS", "bankrupt": False, "liquidating": False,
           "industry_code": "62.010", "industry_label": "Programmeringstjenester", "municipality": "OSLO",
           "municipality_number": "0301", "employees": 3, "website": "", "latest_submitted_accounts": "2025"}
    env = placeholder_envelope("910000012", row, "r", "wall-clock cutoff")
    assert env.run.terminal_status == "partial" and env.operations.requests == 0
    assert env.errors[0]["error"] == "wall-clock cutoff" and not validate_envelope(env.model_dump(mode="json"))
    none = placeholder_envelope("910000012", None, "r", "cutoff")
    assert none.run.terminal_status == "failed" and none.claims[0].availability == "failed"


# ---------- cutoff: partial results written safely ----------
def make_run(n, per_company_cost=1.0, deadline=5.0, expire_at=None):
    now = [0.0]
    budget = Budget(10_000, 15, deadline=deadline, clock=lambda: now[0])
    inputs = [InputRow(o, o, True) for o in orgs(n)]
    fx = load("active_as_with_website")
    seen_plans, calls = [], []

    def make(row, plan):
        now[0] += per_company_cost  # each processed company "takes" this long
        calls.append(row.org)
        if expire_at and len(calls) == expire_at:
            budget.expire()
        client = ApiClient(transport=transport_for({**fx, "org": row.org, "entity": {**fx["entity"],
                           "organisasjonsnummer": row.org}}), budget=budget, sleeper=lambda s: None)
        return register_envelope(row.org, client, run_id="t", modules=("entity",))

    def placeholder(row, reason):
        return placeholder_envelope(row.org, None, "t", reason)

    def plan_fn(pending):
        seen_plans.append((len(pending), budget.remaining_total))
        return {}
    return inputs, budget, make, placeholder, plan_fn, calls, seen_plans


def test_wall_clock_cutoff_writes_exactly_one_envelope_per_input(tmp_path):
    inputs, budget, make, ph, plan_fn, calls, _ = make_run(60, per_company_cost=1.0, deadline=5.0)
    out = tmp_path / "e.jsonl"
    envs, info = run_planned_batch(inputs, make, ph, plan_fn, run_id="t", workers=1, out_path=out, budget=budget,
                                   chunk_size=2)
    assert len(envs) == 60 and info["cutoff_triggered"] and info["placeholders_due_to_cutoff"] > 40
    assert [e.organisation_number for e in envs] == [i.org for i in inputs]
    assert len(calls) < 60  # processing really stopped at the deadline
    lines = out.read_text().splitlines()
    assert len(lines) == 60 and validate_file(out, [i.org for i in inputs])["passed"]
    assert any("cutoff" in e.errors[0]["error"] for e in envs[-5:])


def test_sigterm_style_expire_stops_new_requests_but_every_input_still_answered(tmp_path):
    inputs, budget, make, ph, plan_fn, calls, _ = make_run(30, per_company_cost=0.0, deadline=1e9, expire_at=7)
    envs, info = run_planned_batch(inputs, make, ph, plan_fn, run_id="t", workers=1, out_path=tmp_path / "e.jsonl",
                                   budget=budget, chunk_size=1)
    assert len(envs) == 30 and info["cutoff_triggered"] and len(calls) == 7
    assert all(e.run.terminal_status in ("completed", "partial", "failed") for e in envs)


def test_checkpoint_file_always_holds_every_input(tmp_path):
    inputs, budget, make, ph, plan_fn, *_ = make_run(12, per_company_cost=0.0, deadline=1e9)
    out = tmp_path / "e.jsonl"
    snapshots = []

    def spy_make(row, plan):
        if out.exists():
            snapshots.append(len(out.read_text().splitlines()))
        return make(row, plan)
    run_planned_batch(inputs, spy_make, ph, plan_fn, run_id="t", workers=1, out_path=out, budget=budget,
                      chunk_size=3, min_flush_s=0)
    assert snapshots and all(s == 12 for s in snapshots)  # mid-run kill would still leave 12 envelopes


def test_replanning_sees_the_real_remaining_budget(tmp_path):
    inputs, budget, make, ph, plan_fn, _, seen = make_run(9, per_company_cost=0.0, deadline=1e9)
    run_planned_batch(inputs, make, ph, plan_fn, run_id="t", workers=1, out_path=tmp_path / "e.jsonl", budget=budget,
                      chunk_size=3)
    assert [s[0] for s in seen] == [9, 6, 3] and seen[0][1] > seen[1][1] > seen[2][1]


def test_invalid_ids_get_failed_envelopes_even_after_cutoff(tmp_path):
    inputs, budget, make, ph, plan_fn, *_ = make_run(3, deadline=1e9)
    inputs.append(InputRow("bad", "", False))
    budget.expire()
    envs, _ = run_planned_batch(inputs, make, ph, plan_fn, run_id="t", workers=1, out_path=tmp_path / "e.jsonl",
                                budget=budget)
    assert len(envs) == 4 and envs[3].run.terminal_status == "failed"


def test_in_flight_requests_are_refused_after_expiry_not_hung():
    b = Budget(100, 15)
    client = ApiClient(transport=httpx.MockTransport(lambda r: httpx.Response(200, json={})), budget=b)
    b.expire()
    r = client.get_json("https://data.brreg.no/x", "o")
    assert r.status == -1 and r.error == "budget_exhausted"


# ---------- validator ----------
def good_env():
    fx = load("active_as_with_website")
    env = register_envelope(fx["org"], ApiClient(transport=transport_for(fx)), run_id="t")
    return json.loads(env.to_json_line())


def test_validator_accepts_good_and_rejects_tampered():
    d = good_env()
    assert validate_envelope(d) == []
    Envelope.model_validate(d)
    bad = json.loads(json.dumps(d))
    bad["claims"][0]["evidence_ids"] = ["ev-999"]
    assert any("unknown evidence id" in p for p in validate_envelope(bad))
    bad = json.loads(json.dumps(d))
    rev = next(c for c in bad["claims"] if c["field"] == "financials.revenue")
    next(e for e in bad["evidence"] if e["id"] == rev["evidence_ids"][0])["source_class"] = "company_owned_website"
    assert any("not from the official accounts API" in p for p in validate_envelope(bad))
    rev["reporting_period"] = None
    assert any("without reporting period" in p for p in validate_envelope(bad))
    bad = json.loads(json.dumps(d))
    bad["claims"][1]["availability"] = "maybe"
    assert any("illegal availability" in p for p in validate_envelope(bad))
    bad = json.loads(json.dumps(d))
    bad["claims"].append({"field": "contact_email_1", "value": "x@y.no", "availability": "available",
                          "confidence": 0.8, "evidence_ids": [bad["evidence"][0]["id"]]})
    assert any("snippet does not contain the value" in p for p in validate_envelope(bad))
