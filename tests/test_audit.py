"""Phase 9: automated wrong-company audit and the human review sheet."""
import copy
import csv
import io
import json

import httpx

from signalpost import audit
from signalpost.httpcache import ApiClient
from signalpost.pipeline import register_envelope
from signalpost.web.fetch import WebFetcher  # noqa: F401
from test_register_layer import load, transport_for
from test_updates import PAGE, web_stack

ORG = load("active_as_with_website")["org"]


def verified_envelope():
    """Real pipeline output with a verified website (synthetic page + mock register)."""
    fx = load("active_as_with_website")
    f, _, _ = web_stack([PAGE])
    env = register_envelope(fx["org"], ApiClient(transport=transport_for(fx), sleeper=lambda s: None), run_id="t",
                            fetcher=f, modules=("financials", "entity", "roles", "subunits"))
    return json.loads(env.to_json_line())


def kinds(env, name=None):
    return {f["flag"] for f in audit.audit_envelope(env, name)}


def test_clean_pipeline_output_has_no_hard_flags():
    env = verified_envelope()
    assert any(c["field"] == "official_website" and c["availability"] == "available" for c in env["claims"])
    assert [f for f in audit.audit_envelope(env, "SYNTETISK TESTSELSKAP AS") if f["severity"] == "hard"] == []


def test_web_facts_without_verified_identity_is_flagged():
    env = verified_envelope()
    site = next(c for c in env["claims"] if c["field"] == "official_website")
    site["availability"], site["value"] = "ambiguous", None
    assert "web_facts_without_verified_identity" in kinds(env)


def test_low_identity_confidence_is_flagged_at_threshold():
    env = verified_envelope()
    site = next(c for c in env["claims"] if c["field"] == "official_website")
    site["confidence"] = 0.89
    assert "low_identity_confidence" in kinds(env)
    site["confidence"] = 0.90
    assert "low_identity_confidence" not in kinds(env)


def test_web_fact_from_a_different_domain_is_flagged():
    env = verified_envelope()
    c = next(c for c in env["claims"] if c["field"] == "website_description")
    ev = next(e for e in env["evidence"] if e["id"] == c["evidence_ids"][0])
    ev["source_url"] = "https://other-company.example/about"
    assert "web_source_domain_mismatch" in kinds(env)


def test_register_evidence_naming_another_org_is_flagged():
    env = verified_envelope()
    ev = next(e for e in env["evidence"] if e["source_url"].endswith(f"/enheter/{ORG}"))
    ev["source_url"] = ev["source_url"].replace(ORG, "910000020")
    assert "register_evidence_for_other_org" in kinds(env)


def test_legal_name_differing_from_universe_is_flagged_but_case_and_punctuation_are_not():
    env = verified_envelope()
    assert "legal_name_differs_from_universe" in kinds(env, "NOE ANNET AS")
    assert "legal_name_differs_from_universe" not in kinds(env, "syntetisk  testselskap as.")


def test_financial_value_from_non_official_source_is_flagged():
    env = verified_envelope()
    c = next(c for c in env["claims"] if c["field"] == "financials.revenue")
    next(e for e in env["evidence"] if e["id"] == c["evidence_ids"][0])["source_class"] = "company_owned_website"
    assert "financial_not_from_official_api" in kinds(env)


def test_foreign_org_number_in_web_snippet_is_a_soft_flag():
    env = verified_envelope()
    c = next(c for c in env["claims"] if c["field"] == "website_description")
    ev = next(e for e in env["evidence"] if e["id"] == c["evidence_ids"][0])
    ev["claim_span"] += " Org.nr 910 000 020"
    fl = audit.audit_envelope(env)
    soft = [f for f in fl if f["flag"] == "foreign_org_number_in_web_snippet"]
    assert soft and soft[0]["severity"] == "soft"


def test_register_only_profile_with_no_website_is_clean():
    fx = load("enk_no_accounts")
    env = json.loads(register_envelope(fx["org"], ApiClient(transport=transport_for(fx)), run_id="t").to_json_line())
    assert audit.audit_envelope(env) == []


def test_audit_file_counts_and_pass_fail(tmp_path):
    good, bad = verified_envelope(), verified_envelope()
    bad["organisation_number"] = "910000020"
    next(c for c in bad["claims"] if c["field"] == "official_website")["confidence"] = 0.5
    p = tmp_path / "p.jsonl"
    p.write_text(json.dumps(good) + "\n" + json.dumps(bad) + "\n")
    res = audit.audit_file(p, {ORG: "SYNTETISK TESTSELSKAP AS"})
    assert res["profiles"] == 2 and res["profiles_with_verified_website"] == 2
    assert not res["passed"] and res["by_flag"]["low_identity_confidence"] == 1 and res["hard_flags"] >= 1
    p.write_text(json.dumps(good) + "\n")
    assert audit.audit_file(p)["passed"]


# ---------- review sheet ----------
def make_envs(n_web, n_plain):
    web = verified_envelope()
    fx = load("enk_no_accounts")
    plain = json.loads(register_envelope(fx["org"], ApiClient(transport=httpx.MockTransport(transport_for(fx).handle_request)),
                                         run_id="t").to_json_line())
    envs = []
    for i in range(n_web):
        e = copy.deepcopy(web)
        e["organisation_number"] = f"91{i:07d}"
        envs.append(e)
    for i in range(n_plain):
        e = copy.deepcopy(plain)
        e["organisation_number"] = f"92{i:07d}"
        envs.append(e)
    return envs


def has_site(e):
    return any(c["field"] == "official_website" and c["availability"] == "available" for c in e["claims"])


def test_pick_is_seeded_and_prioritises_web_profiles():
    envs = make_envs(40, 200)
    a, b = audit.pick_profiles(envs, 50, seed=1), audit.pick_profiles(envs, 50, seed=1)
    assert [e["organisation_number"] for e in a] == [e["organisation_number"] for e in b] and len(a) == 50
    assert sum(has_site(e) for e in a) == 25 and len({e["organisation_number"] for e in a}) == 50
    assert audit.pick_profiles(envs, 50, seed=2) != a
    few = audit.pick_profiles(make_envs(3, 100), 50, seed=1)
    assert sum(has_site(e) for e in few) == 3 and len(few) == 50
    assert len(audit.pick_profiles(make_envs(2, 3), 50)) == 5  # fewer profiles than k: take all


def test_sheet_has_register_and_web_rows_with_source_and_snippet():
    env = verified_envelope()
    md, csv_text = audit.render_sheet([env], {})
    rows = list(csv.DictReader(io.StringIO(csv_text)))
    layers = {r["layer"] for r in rows}
    assert layers == {"REGISTER", "WEB"}
    desc = next(r for r in rows if r["field"] == "website_description")
    assert desc["source_url"].startswith("https://www.syntetisk-test.example") and "programvare" in desc["evidence_snippet"]
    assert any(r["field"] == "legal_name" and r["value"] == "SYNTETISK TESTSELSKAP AS" for r in rows)
    assert "verdict (ok / wrong company / wrong value / unsupported)" in rows[0]
    assert f"<https://data.brreg.no/enhetsregisteret/api/enheter/{env['organisation_number']}>" in md
    assert "| WEB | website_description |" in md and "## SYNTETISK TESTSELSKAP AS" in md


def test_sheet_shows_flags_next_to_the_company():
    env = verified_envelope()
    next(c for c in env["claims"] if c["field"] == "official_website")["confidence"] = 0.5
    flags = audit.audit_envelope(env)
    md, _ = audit.render_sheet([env], {ORG: flags})
    assert "**HARD flag** `low_identity_confidence`" in md
