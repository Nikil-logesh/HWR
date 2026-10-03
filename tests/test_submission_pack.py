"""Phase 10: kit-compatible CLI flags, fresh-clone robustness, HTML report safety, secrets hygiene."""
import json
import re
from pathlib import Path

import httpx

from signalpost import cli, htmlreport
from signalpost.httpcache import ApiClient
from signalpost.inputs import load_registry_rows
from signalpost.pipeline import register_envelope
from signalpost.web.llm import LlmClient
from test_register_layer import load, transport_for
from test_updates import PAGE, web_stack

ORG = load("active_as_with_website")["org"]
ROOT = Path(__file__).parents[1]


def patch_api(monkeypatch, fx=None):
    fx = fx or load("active_as_with_website")
    monkeypatch.setattr(cli, "ApiClient", lambda budget=None: ApiClient(transport=transport_for(fx), budget=budget,
                                                                        sleeper=lambda s: None))
    monkeypatch.chdir(ROOT)


# ---------- kit-compatible flags ----------
def test_kit_style_flags_write_to_the_requested_paths(monkeypatch, tmp_path):
    patch_api(monkeypatch)
    inp = tmp_path / "in.txt"
    inp.write_text(f"{ORG}\n")
    rc = cli.main(["run", "--organisations", str(inp), "--bulk", str(tmp_path / "nope.csv"), "--no-web", "--quiet",
                   "--output", str(tmp_path / "x" / "env.jsonl"), "--profiles-output", str(tmp_path / "y" / "prof.jsonl"),
                   "--report", str(tmp_path / "z" / "rep.json"), "--run-id", "smoke-001", "--expected-count", "1",
                   "--resume", "--checkpoint-every", "25", "--out", str(tmp_path / "o")])
    assert rc == 0
    env = (tmp_path / "x" / "env.jsonl").read_text()
    assert (tmp_path / "y" / "prof.jsonl").read_text() == env and len(env.splitlines()) == 1
    assert json.loads((tmp_path / "z" / "rep.json").read_text())["run_id"] == "smoke-001"
    assert (tmp_path / "o" / "report.html").exists()


def test_html_can_be_disabled(monkeypatch, tmp_path):
    patch_api(monkeypatch)
    inp = tmp_path / "in.txt"
    inp.write_text(f"{ORG}\n")
    assert cli.main(["run", "--organisations", str(inp), "--out", str(tmp_path / "o"), "--no-web", "--quiet",
                     "--html", "none", "--bulk", str(tmp_path / "n")]) == 0
    assert not (tmp_path / "o" / "report.html").exists()


# ---------- fresh clone without git-lfs ----------
def test_git_lfs_pointer_as_registry_file_is_survivable(tmp_path, capsys):
    ptr = tmp_path / "orgs.json"
    ptr.write_text("version https://git-lfs.github.com/spec/v1\noid sha256:abc\nsize 131374513\n")
    assert load_registry_rows(ptr, {ORG}) == {}
    assert "LFS" in capsys.readouterr().err


def test_default_registry_pointer_does_not_crash_a_run(monkeypatch, tmp_path):
    patch_api(monkeypatch)
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "orgs.json").write_text("version https://git-lfs.github.com/spec/v1\noid sha256:a\nsize 1\n")
    monkeypatch.chdir(tmp_path)
    inp = tmp_path / "in.txt"
    inp.write_text(f"{ORG}\n")
    assert cli.main(["run", "--organisations", str(inp), "--out", str(tmp_path / "o"), "--no-web", "--quiet"]) == 0
    line = json.loads((tmp_path / "o" / "envelopes.jsonl").read_text().splitlines()[0])
    assert line["run"]["terminal_status"] == "completed"


# ---------- HTML report ----------
def sample_envs(name="SYNTETISK TESTSELSKAP AS"):
    fx = load("active_as_with_website")
    f, _, _ = web_stack([PAGE])
    env = register_envelope(fx["org"], ApiClient(transport=transport_for(fx), sleeper=lambda s: None), run_id="t",
                            fetcher=f, modules=("financials", "entity", "roles", "subunits"))
    return [json.loads(env.to_json_line())]


REPORT = {"run_id": "r1", "completed_at": "2026-10-03T00:00:00Z", "envelopes_written": 1, "changes_total": 0,
          "operations": {"requests_total_budgeted": 7, "wall_clock_seconds": 1.5, "third_party_cost_usd": 0.0},
          "coverage_pct": {"legal_name": 100.0}}


def test_html_report_shows_facts_sources_snippets_and_explanation():
    page = htmlreport.render(sample_envs(), REPORT)
    assert page.startswith("<!doctype html>") and 'name="viewport"' in page and "prefers-color-scheme" in page
    for needle in ("SYNTETISK TESTSELSKAP AS", "12 500 000 NOK", "period 2025-01-01/2025-12-31", "Kari Nordmann",
                   "website verified", "data.brreg.no", "evidence</summary>", "Search name or organisation number",
                   "Verified website", "never as zero"):
        assert needle in page, needle
    assert "http://" not in re.sub(r"<script>.*?</script>", "", page, flags=re.DOTALL).replace("http://www.w3.org", "")


def test_html_report_escapes_hostile_third_party_text():
    envs = sample_envs()
    evil = '<img src=x onerror=alert(1)>'
    for c in envs[0]["claims"]:
        if c["field"] == "website_description":
            c["value"] = evil
    envs[0]["explanation"] = f'{evil} </details><script>alert(2)</script>'
    envs[0]["evidence"][0]["claim_span"] = '"><script>alert(3)</script>'
    envs[0]["evidence"][1]["source_url"] = 'javascript:alert(4)'
    page = htmlreport.render(envs, REPORT)
    stripped = htmlreport.strip_scripts(page)
    assert "<img src=x" not in stripped and "<script>alert" not in page and "onerror=alert(1)>" not in stripped
    assert 'href="javascript:' not in page and "&lt;img src=x onerror=alert(1)&gt;" in page
    assert page.count("<script>") == 1  # only our own inline filter script


def test_html_report_caps_size_and_prioritises_interesting_profiles():
    base = sample_envs()[0]
    envs = []
    for i in range(30):
        e = json.loads(json.dumps(base))
        e["organisation_number"] = f"9{i:08d}"
        e["run"]["terminal_status"] = "failed" if i == 29 else "completed"
        envs.append(e)
    page = htmlreport.render(envs, REPORT, max_companies=5)
    assert page.count('<details class="co"') == 5 and "Showing 5 of 30" in page
    assert "900000029" in page  # the failed profile is shown first
    assert "No companies." in htmlreport.render([], REPORT)


def test_safe_url():
    assert htmlreport.safe_url("https://a.no/x") and htmlreport.safe_url("http://a.no")
    assert not htmlreport.safe_url("javascript:alert(1)") and not htmlreport.safe_url("data:text/html,x")
    assert not htmlreport.safe_url("") and not htmlreport.safe_url(None)


# ---------- secrets never reach outputs ----------
def test_api_keys_never_appear_in_envelopes_report_or_html(monkeypatch, tmp_path):
    secret = "sk-SECRET-123456"
    patch_api(monkeypatch)
    monkeypatch.setenv("LLM_PRIMARY_BASE_URL", "https://llm.example/v1")
    monkeypatch.setenv("LLM_PRIMARY_MODEL", "m")
    monkeypatch.setenv("LLM_PRIMARY_API_KEY", secret)
    f, _, _ = web_stack([PAGE])
    monkeypatch.setattr(cli, "WebFetcher", lambda budget: f)
    monkeypatch.setattr(cli, "LlmClient", lambda providers, budget: LlmClient(
        providers, budget, transport=httpx.MockTransport(lambda r: httpx.Response(401, text=f"bad key {secret}"))))
    inp = tmp_path / "in.txt"
    inp.write_text(f"{ORG}\n")
    out = tmp_path / "o"
    assert cli.main(["run", "--organisations", str(inp), "--out", str(out), "--quiet", "--bulk", str(tmp_path / "n")]) == 0
    blob = "".join(p.read_text() for p in out.iterdir() if p.suffix in (".jsonl", ".json", ".html"))
    assert secret not in blob and "Bearer" not in blob and len(blob) > 1000


# ---------- bulk file sniffing (the kit saves the gzip download as .csv) ----------
def _csv_text(delim=","):
    lines = (ROOT / "tests" / "fixtures" / "recorded" / "bulk_rows.csv").read_text(encoding="utf-8").splitlines()
    if delim == ",":
        return "\n".join(lines) + "\n"
    import csv
    import io
    rows = list(csv.reader(io.StringIO("\n".join(lines))))
    out = io.StringIO()
    csv.writer(out, delimiter=delim, lineterminator="\n").writerows(rows)
    return out.getvalue()


def test_bulk_file_is_detected_by_content_not_extension(tmp_path):
    import gzip
    want = {"923609016"}
    plain = tmp_path / "plain.csv"
    plain.write_text(_csv_text(), encoding="utf-8")
    gz_named_csv = tmp_path / "enheter.csv"  # exactly what the kit README produces: gzip bytes, .csv name
    gz_named_csv.write_bytes(gzip.compress(_csv_text().encode("utf-8")))
    gz = tmp_path / "enheter.csv.gz"
    gz.write_bytes(gzip.compress(_csv_text().encode("utf-8")))
    bom = tmp_path / "bom.csv"
    bom.write_bytes(b"\xef\xbb\xbf" + _csv_text().encode("utf-8"))
    semi = tmp_path / "semi.csv"
    semi.write_text(_csv_text(";"), encoding="utf-8")
    for f in (plain, gz_named_csv, gz, bom, semi):
        rows = load_registry_rows(f, want)
        assert rows["923609016"]["name"] == "EQUINOR ASA", f.name
        assert rows["923609016"]["_entity"]["forretningsadresse"]["poststed"] == "STAVANGER", f.name


def test_universe_jsonl_gz_and_garbage_files(tmp_path, capsys):
    import gzip
    row = {"organisation_number": ORG, "name": "X AS", "legal_form": "AS", "employees": None, "bankrupt": False,
           "liquidating": False, "municipality": "OSLO", "municipality_number": "0301", "industry_code": "62.010",
           "industry_label": "x", "website": "", "latest_submitted_accounts": "2025"}
    f = tmp_path / "u.jsonl.gz"
    f.write_bytes(gzip.compress((json.dumps(row) + "\n").encode()))
    assert load_registry_rows(f, {ORG})[ORG]["name"] == "X AS"
    junk = tmp_path / "junk.csv"
    junk.write_bytes(b"\xff\xfe\x00garbage\x00\x01")
    assert load_registry_rows(junk, {ORG}) == {} and "unusable" in capsys.readouterr().err


def test_escaped_quotes_and_malformed_rows_do_not_break_the_bulk_loader(tmp_path):
    """Regression: csv.Sniffer picked doublequote=False on the real file, breaking rows with escaped quotes."""
    import csv
    import io

    from signalpost.inputs import csv_row_to_entity
    src = list(csv.reader(io.StringIO((ROOT / "tests/fixtures/recorded/bulk_rows.csv").read_text(encoding="utf-8"))))
    header = src[0]
    quoted = next(r for r in src[1:] if r[0] == "923609016")
    quoted[header.index("navn")] = 'EQUINOR "THE ""BIG"" ONE" ASA, Norge'
    quoted[header.index("vedtektsfestetFormaal")] = 'Line one\nLine "two"; with, commas'
    out = io.StringIO()
    csv.writer(out, lineterminator="\n").writerows([header, quoted])
    f = tmp_path / "q.csv"
    f.write_text(out.getvalue(), encoding="utf-8")
    row = load_registry_rows(f, {"923609016"})["923609016"]
    assert row["name"] == 'EQUINOR "THE ""BIG"" ONE" ASA, Norge'
    assert row["_entity"]["vedtektsfestetFormaal"] == 'Line one\nLine "two"; with, commas'
    # a row with more cells than the header must be tolerated, not crash
    f2 = tmp_path / "x.csv"
    f2.write_text(out.getvalue().rstrip("\n") + ",EXTRA,CELLS\n", encoding="utf-8")
    assert load_registry_rows(f2, {"923609016"})["923609016"]["name"]
    assert csv_row_to_entity({"a": "1", None: ["x"], "b": None}) == {"a": "1"}
