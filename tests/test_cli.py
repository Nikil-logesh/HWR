"""Phase 6: inputs, one-envelope-per-input guarantee, explanations, CLI end to end (mock network)."""
import gzip
import json
import re
from pathlib import Path

import httpx
import pytest

from signalpost import cli
from signalpost.explain import explain
from signalpost.httpcache import ApiClient
from signalpost.inputs import InputRow, read_inputs
from signalpost.models import Envelope, Run
from signalpost.runner import failed_envelope, run_batch
from test_register_layer import NAMES, load, run, transport_for

ORG = load("active_as_with_website")["org"]


# ---------- inputs ----------
def test_read_inputs_formats_dedupe_and_invalid_kept(tmp_path):
    (tmp_path / "a.txt").write_text(f"{ORG}\n910 000 012\n123\n\nabc\n")
    rows = read_inputs(tmp_path / "a.txt")
    assert [r.org for r in rows] == [ORG, "123", ""] and [r.valid for r in rows] == [True, False, False]
    (tmp_path / "b.jsonl").write_text(json.dumps({"organisation_number": ORG, "sample_slice": "x"}) + "\n")
    assert read_inputs(tmp_path / "b.jsonl")[0].extra == {"sample_slice": "x"}
    (tmp_path / "c.json").write_text(json.dumps([ORG, {"organisasjonsnummer": "910000020"}]))
    assert len(read_inputs(tmp_path / "c.json")) == 2
    with gzip.open(tmp_path / "d.jsonl.gz", "wt") as fh:
        fh.write(json.dumps({"organisation_number": ORG}) + "\n")
    assert read_inputs(tmp_path / "d.jsonl.gz")[0].valid


# ---------- one terminal envelope per input ----------
def test_runner_always_returns_one_envelope_per_input_in_order(tmp_path):
    inputs = [InputRow(ORG, ORG, True), InputRow("123", "123", False), InputRow("x", "910000020", True),
              InputRow("y", "910000039", True)]
    good = run("active_as_with_website")[1]

    def make(row):
        if row.org == "910000020":
            raise RuntimeError("boom")
        return good if row.org == ORG else failed_envelope(row, "t", "x")
    out = tmp_path / "e.jsonl"
    envs = run_batch(inputs, make, run_id="t", workers=3, out_path=out, checkpoint_every=1)
    assert [e.organisation_number for e in envs] == [ORG, "123", "910000020", "910000039"]
    assert envs[1].run.terminal_status == "failed" and "invalid organisation number" in envs[1].errors[0]["error"]
    assert "RuntimeError: boom" in envs[2].errors[0]["error"] and envs[2].claims[0].availability == "failed"
    lines = out.read_text().splitlines()
    assert len(lines) == 4 and all(Envelope.model_validate_json(ln) for ln in lines)
    assert not out.with_suffix(".jsonl.tmp").exists()


# ---------- explanations ----------
def sentences(text):
    return [s for s in re.split(r"(?<=\.)\s+(?=[A-Z])", text) if s]


@pytest.mark.parametrize("name", NAMES)
def test_explanation_is_short_and_every_number_is_supported_by_a_claim(name):
    _, env = run(name)
    text = explain(env)
    assert 2 <= len(sentences(text)) <= 4, text
    haystack = json.dumps([c.model_dump() for c in env.claims] + [e.model_dump() for e in env.evidence],
                          ensure_ascii=False)
    haystack = haystack.replace("\\u00a0", " ")
    for num in re.findall(r"\d[\d ]*\d|\d", text):
        plain = num.strip()
        assert plain.replace(" ", "") in haystack.replace(" ", "") or plain in haystack, (num, text)


def test_explanation_content_for_key_cases():
    assert "Latest filed accounts (2025-01-01/2025-12-31): revenue 12 500 000 NOK" in explain(run("active_as_with_website")[1])
    assert "registered as bankrupt" in explain(run("bankrupt_as")[1])
    t = explain(run("enk_no_accounts")[1])
    assert "no annual accounts" in t and "unknown, not zero" in t
    assert "not found or has been deleted" in explain(run("deleted_entity_410")[1])
    assert "confidence 0.99" in explain(run("active_as_with_website")[1])
    assert "hiring and dated public activity were not collected" in t


def test_explanation_reports_conflict_between_website_and_register():
    from signalpost.claims import ClaimSet
    cs = ClaimSet()
    kw = {"source_url": "https://x.example/", "source_class": "company_owned_website",
          "retrieved_at": "2026-10-03T00:00:00Z", "sha256": "a", "span": "s", "method": "m"}
    cs.available("legal_name", "NORDVIK BYGG AS", confidence=0.99, **kw)
    cs.available("phone", "70 12 34 56", confidence=0.99, **kw)
    cs.available("official_website", "https://nordvik.example/", confidence=1.0, **{**kw, "method": "identity_gate:organisation_number"})
    cs.available("contact_phone_1", "55 11 22 33", confidence=0.85, **kw)
    from signalpost.models import Envelope as E
    env = E(organisation_number="910000012", run=Run(run_id="r", started_at="a", completed_at="b", terminal_status="completed"),
            claims=cs.sorted_claims(), evidence=cs.evidence)
    assert "Conflict: the phone number on the site (55 11 22 33) differs from the register (70 12 34 56)" in explain(env)


# ---------- CLI end to end ----------
@pytest.fixture
def patched(monkeypatch):
    fx = load("active_as_with_website")
    monkeypatch.setattr(cli, "ApiClient", lambda budget=None: ApiClient(transport=transport_for(fx), budget=budget,
                                                                        sleeper=lambda s: None))
    monkeypatch.chdir(Path(__file__).parents[1])
    return fx


def test_cli_run_writes_envelopes_report_and_exit_code(patched, tmp_path, capsys):
    inp = tmp_path / "in.txt"
    inp.write_text(f"{ORG}\n123\n{ORG}\n")  # duplicate dropped, invalid kept
    out = tmp_path / "out"
    rc = cli.main(["run", "--organisations", str(inp), "--out", str(out), "--no-web", "--quiet",
                   "--bulk", str(tmp_path / "missing.jsonl")])
    assert rc == 0
    envs = [json.loads(ln) for ln in (out / "envelopes.jsonl").read_text().splitlines()]
    assert [e["organisation_number"] for e in envs] == [ORG, "123"]
    assert envs[0]["explanation"] and envs[1]["run"]["terminal_status"] == "failed"
    rep = json.loads((out / "report.json").read_text())
    assert rep["exactly_one_envelope_per_input"] and rep["envelopes_written"] == 2
    assert rep["operations"]["requests_total_budgeted"] == 4 and rep["operations"]["third_party_cost_usd"] == 0
    assert rep["coverage_companies_with_field"]["legal_name"] == 1
    assert (out / "state.sqlite").exists() and "Coverage" in capsys.readouterr().out


def test_cli_expected_count_mismatch_exits_2(patched, tmp_path):
    inp = tmp_path / "in.txt"
    inp.write_text(f"{ORG}\n")
    assert cli.main(["run", "--organisations", str(inp), "--out", str(tmp_path / "o"), "--expected-count", "5"]) == 2


def test_cli_previous_file_drives_change_detection(patched, tmp_path, monkeypatch):
    inp = tmp_path / "in.txt"
    inp.write_text(f"{ORG}\n")
    a, b = tmp_path / "a", tmp_path / "b"
    args = ["run", "--organisations", str(inp), "--no-web", "--quiet", "--bulk", str(tmp_path / "none")]
    assert cli.main([*args, "--out", str(a), "--run-id", "r1"]) == 0
    changed = json.loads(json.dumps(patched))
    changed["entity"]["konkurs"] = True
    monkeypatch.setattr(cli, "ApiClient", lambda budget=None: ApiClient(transport=transport_for(changed), budget=budget,
                                                                        sleeper=lambda s: None))
    assert cli.main([*args, "--out", str(b), "--run-id", "r2", "--previous", str(a / "envelopes.jsonl")]) == 0
    env = json.loads((b / "envelopes.jsonl").read_text())
    assert [c["field"] for c in env["changes"]] == ["status"] and "material: status" in env["explanation"]
    assert json.loads((b / "report.json").read_text())["changes_total"] == 1


def test_register_fallback_from_universe_file_when_api_fails(monkeypatch, tmp_path):
    row = {"organisation_number": ORG, "name": "SYNTETISK TESTSELSKAP AS", "legal_form": "AS", "employees": None,
           "bankrupt": False, "liquidating": False, "municipality": "OSLO", "municipality_number": "0301",
           "industry_code": "62.010", "industry_label": "Programmeringstjenester", "website": "",
           "latest_submitted_accounts": "2025"}
    uni = tmp_path / "u.jsonl"
    uni.write_text(json.dumps(row) + "\n")
    monkeypatch.setattr(cli, "ApiClient", lambda budget=None: ApiClient(
        transport=httpx.MockTransport(lambda r: httpx.Response(503)), budget=budget, sleeper=lambda s: None))
    inp = tmp_path / "in.txt"
    inp.write_text(f"{ORG}\n")
    assert cli.main(["run", "--organisations", str(inp), "--out", str(tmp_path / "o"), "--bulk", str(uni), "--no-web",
                     "--quiet"]) == 0
    env = json.loads((tmp_path / "o" / "envelopes.jsonl").read_text())
    c = {x["field"]: x for x in env["claims"]}
    assert c["legal_name"]["value"] == "SYNTETISK TESTSELSKAP AS" and c["legal_name"]["availability"] == "available"
    assert c["financials"]["availability"] == "failed" and env["run"]["terminal_status"] == "partial"
