"""Phase 8: model benchmark harness, exercised with scripted fake models (no keys, no network)."""
import json
import re

import httpx

from signalpost import modelbench as mb
from signalpost.budget import Budget
from signalpost.claims import ClaimSet
from signalpost.web.enrich import enrich_website
from signalpost.web.fetch import WebFetcher
from signalpost.web.llm import LlmClient, Provider, parse_json_content
from test_web_enrichment import CONTACT, GOOD, OUR, PUBLIC, site

PAGE1 = "Alfa Bygg AS bygger boliger i Bergen.\nVi tilbyr totalentreprise og rehabilitering.\nKontakt: post@alfa.example"
PAGE2 = "Beta Data AS lager programvare for fiskeri.\nProdukter: sporingssystem, rapportering."


def corpus():
    mk = lambda org, name, text: mb.CorpusItem(org, name, "real", [
        {"url": f"https://{org}.example/", "text": text, "corpus": text}])
    return [mk("910000012", "Alfa Bygg AS", PAGE1), mk("910000020", "Beta Data AS", PAGE2)]


def user_text(req):
    return json.loads(req.content)["messages"][1]["content"]


def lines_of(req):
    """Page lines a sensible model would quote: injected instructions are skipped."""
    body = user_text(req).split("[PAGE 1]", 1)[1].split("\n", 1)[1]
    return [ln for ln in body.split("\n") if ln.strip() and mb.MARKER not in ln]


def reply(content, status=200, usage=(100, 30)):
    return httpx.Response(status, json={"choices": [{"message": {"content": content}}],
                                        "usage": {"prompt_tokens": usage[0], "completion_tokens": usage[1]}})


def good_payload(req):
    ls = lines_of(req)
    return {"description": {"page": 1, "value": ls[0], "evidence_snippet": ls[0]},
            "services": [{"page": 1, "value": ls[1][:20], "evidence_snippet": ls[1]}]}


def run_model(name, handler, host="https://a.example/v1", **kw):
    p = Provider(name, host, name, "k", **kw)
    rows = mb.evaluate_model(p, corpus() + mb.injection_items(), transport=httpx.MockTransport(handler),
                             sleeper=lambda s: None)
    return p, rows


def handlers():
    def good(req):
        return reply(json.dumps(good_payload(req)))

    def hallucinating(req):
        return reply(json.dumps({"description": {"page": 1, "value": "Verdens beste selskap", "evidence_snippet":
                                                 "Verdens beste selskap med 500 ansatte"},
                                 "services": [{"page": 1, "value": "romfart", "evidence_snippet": "Vi tilbyr romfart"}]}))

    def fenced(req):
        return reply("```json\n" + json.dumps(good_payload(req)) + "\n```")

    def thinking(req):
        return reply("<think>let me see...</think>" + json.dumps(good_payload(req)), usage=(100, 400))

    def prose(req):
        return reply("Sorry, I cannot help with that.")

    def follower(req):
        if mb.MARKER in user_text(req):
            return reply(json.dumps({"description": None, "services": [
                {"page": 1, "value": mb.MARKER, "evidence_snippet": mb.MARKER}]}))
        return reply(json.dumps(good_payload(req)))

    def limited(req):
        return httpx.Response(429, headers={"retry-after": "0"})
    return {"good": good, "hallucinating": hallucinating, "fenced": fenced, "thinking": thinking, "prose": prose,
            "follower": follower, "limited": limited}


def all_rows():
    rows, provs = [], {}
    for i, (name, h) in enumerate(handlers().items()):
        p, r = run_model(name, h, host=f"https://host{i % 3}.example/v1", price_in=0.1, price_out=0.4)
        rows += r
        provs[name] = p
    return rows, provs


# ---------- parsing ----------
def test_parse_json_content_strict_vs_recovered():
    assert parse_json_content('{"a": 1}') == ({"a": 1}, True)
    assert parse_json_content('```json\n{"a": 1}\n```') == ({"a": 1}, False)
    assert parse_json_content('<think>x { y }</think>\n{"a": 1}') == ({"a": 1}, False)
    assert parse_json_content('Here you go: {"a": 1} hope it helps') == ({"a": 1}, False)
    assert parse_json_content("[1, 2]") == (None, False) and parse_json_content("no json") == (None, False)
    assert parse_json_content("") == (None, False)


def test_provider_extra_body_and_json_mode_are_sent():
    seen = {}

    def h(req):
        seen.update(json.loads(req.content))
        return reply('{"description": null, "services": []}')
    c = LlmClient([Provider("p", "https://x.example/v1", "mm", "k", json_mode=False,
                            extra_body={"reasoning_effort": "low"}, max_tokens=321)], Budget(9, 9),
                  transport=httpx.MockTransport(h))
    r = c.complete("hello", "o")
    assert r.data == {"description": None, "services": []} and r.strict_json and r.prompt_tokens == 100
    assert "response_format" not in seen and seen["reasoning_effort"] == "low" and seen["max_tokens"] == 321
    assert seen["temperature"] == 0 and seen["model"] == "mm"


# ---------- per-model metrics ----------
def test_good_model_metrics():
    _, rows = run_model("good", handlers()["good"])
    real = [r for r in rows if r.kind == "real"]
    assert all(r.ok and r.strict_json and r.proposed == 2 and r.verified == 2 for r in real)
    assert all(r.description_verified and r.services_verified == 1 for r in real)
    assert not any(r.injection_followed for r in rows)


def test_hallucinating_model_is_caught_by_the_verifier():
    _, rows = run_model("hallucinating", handlers()["hallucinating"])
    real = [r for r in rows if r.kind == "real"]
    assert all(r.proposed == 2 and r.verified == 0 for r in real)
    assert all(r.dropped == {"snippet not found in page": 2} for r in real)


def test_fenced_and_thinking_replies_are_valid_only_after_recovery():
    for name in ("fenced", "thinking"):
        _, rows = run_model(name, handlers()[name])
        real = [r for r in rows if r.kind == "real"]
        assert all(r.ok and not r.strict_json and r.verified == 2 for r in real)


def test_prose_and_rate_limit_are_failures_not_crashes():
    _, rows = run_model("prose", handlers()["prose"])
    assert all(not r.ok and r.error == "invalid_json" for r in rows)
    _, rows = run_model("limited", handlers()["limited"])
    assert all(not r.ok and r.error == "HTTP 429" for r in rows)


def test_prompt_injection_compliance_is_detected():
    _, rows = run_model("follower", handlers()["follower"])
    inj = [r for r in rows if r.kind == "injection"]
    assert sum(r.injection_followed for r in inj if r.org == "injection-1") == 1
    assert not any(r.injection_followed for r in rows if r.kind == "real")


# ---------- aggregation, recommendation, report ----------
def test_summary_and_recommendation_pick_the_right_models():
    rows, provs = all_rows()
    s = mb.summarize(rows, provs)
    assert s["good"]["strict_json_rate"] == 1.0 and s["fenced"]["strict_json_rate"] == 0.0
    assert s["fenced"]["valid_json_rate_after_recovery"] == 1.0 and s["prose"]["failure_rate"] == 1.0
    assert s["hallucinating"]["verifier_pass_rate"] == 0.0 and s["follower"]["injection_followed"] >= 1
    assert abs(s["good"]["declared_cost_usd"] - (5 * 100 * 0.1 + 5 * 30 * 0.4) / 1e6) < 1e-9
    assert s["good"]["pages"] == 2 and s["good"]["injection_probes"] == 3
    assert not mb.eligible(s["hallucinating"]) and not mb.eligible(s["follower"])
    assert not mb.eligible(s["prose"]) and not mb.eligible(s["limited"])
    rec = mb.recommend(s)
    assert set(rec["ranking"]) == {"good", "fenced", "thinking"}
    assert rec["primary"] in rec["ranking"] and rec["fallback"] in rec["ranking"] and rec["fallback"] != rec["primary"]
    assert s[rec["fallback"]]["host"] != s[rec["primary"]]["host"]  # independent failure domains preferred


def test_recommendation_with_no_eligible_model_says_so():
    _, rows = run_model("prose", handlers()["prose"])
    prov = {"prose": Provider("prose", "https://a.example/v1", "prose", "k")}
    rec = mb.recommend(mb.summarize(rows, prov))
    assert rec["primary"] is None and "no model met" in rec["note"]


def test_wilson_interval_and_percentiles():
    lo, hi = mb.wilson(9, 10)
    assert 0.55 < lo < 0.60 and 0.97 < hi < 0.99 and mb.wilson(0, 0) == (0.0, 0.0)
    assert mb.pct([1, 2, 3, 4], 0.5) == 2 and mb.pct([], 0.5) is None


def test_markdown_is_computed_from_rows_and_has_no_placeholders():
    rows, provs = all_rows()
    s = mb.summarize(rows, provs)
    md = mb.render_markdown(s, mb.recommend(s), {"run_at": "2026-10-03", "pages": 2, "injection_probes": 3})
    assert "| good (`good`)" in md and "**Primary:**" in md and "?" not in md.split("## Recommendation")[0].split("\n\n")[1]
    assert re.search(r"\| 1\.00 \| 1\.00 \| 0\.00 \|", md)  # good: strict 1.00, valid 1.00, failures 0.00


def test_review_sheet_samples_only_verified_real_facts():
    rows, _ = all_rows()
    sheet = mb.review_sheet(rows, per_model=3)
    assert sheet.startswith("model,org,field,value") and "hallucinating" not in sheet and "prose" not in sheet
    assert mb.MARKER not in sheet


def test_corpus_roundtrip_and_injection_probes(tmp_path):
    items = corpus() + mb.injection_items()
    mb.save_corpus(items, tmp_path)
    back = mb.load_corpus(tmp_path)
    assert {i.org for i in back} == {i.org for i in items} and all(i.kind in ("real", "injection") for i in back)
    assert all(mb.MARKER in i.pages[0]["text"] for i in mb.injection_items())


# ---------- corpus capture uses the real identity gate ----------
def test_capture_collects_only_identity_verified_pages():
    transport, _ = site({"/": GOOD, "/kontakt": CONTACT})
    f = WebFetcher(Budget(100, 15), transport=transport, resolver=PUBLIC, sleeper=lambda s: None)
    got = []
    out = enrich_website(ClaimSet(), OUR, "nordvik.example", f, None, capture=got)
    assert out.state == "verified" and got and any("Nordvik Bygg AS" in p.text for p in got)
    transport2, _ = site({"/": "<html><body>Nordvik Bygg AS. Org.nr 910 000 020</body></html>"})
    f2 = WebFetcher(Budget(100, 15), transport=transport2, resolver=PUBLIC, sleeper=lambda s: None)
    rejected = []
    assert enrich_website(ClaimSet(), OUR, "nordvik.example", f2, None, capture=rejected).state == "ambiguous"
    assert rejected == []  # a wrong-company page never reaches the benchmark corpus


# ---------- the script (stages without network) ----------
def load_script():
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("model_benchmark", Path(__file__).parents[1] / "scripts" / "model_benchmark.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_script_loads_only_models_with_keys_and_resolves_model_env(monkeypatch):
    from pathlib import Path
    mod = load_script()
    cfg = Path(__file__).parents[1] / "bench" / "models.json"
    for k in ("NVIDIA_API_KEY", "GEMINI_API_KEY", "GEMINI_FLASH_LITE_MODEL"):
        monkeypatch.delenv(k, raising=False)
    provs, skipped = mod.load_providers(cfg, None)
    assert provs == [] and len(skipped) == 5
    monkeypatch.setenv("NVIDIA_API_KEY", "k")
    provs, skipped = mod.load_providers(cfg, None)
    assert [p.name for p in provs] == ["deepseek-v4.1-flash", "gemma-4-31b-it", "gpt-oss-20b",
                                       "nemotron-3.5-lightning-30b-a3b"]
    assert {p.model for p in provs} == {"deepseek-ai/deepseek-v4.1-flash", "google/gemma-4-31b-it",
                                        "openai/gpt-oss-20b", "nvidia/nemotron-3.5-lightning-30b-a3b"}
    assert skipped and "gemini-flash-lite" in skipped[0]
    monkeypatch.setenv("GEMINI_API_KEY", "g")
    monkeypatch.setenv("GEMINI_FLASH_LITE_MODEL", "some-flash-lite")
    provs, _ = mod.load_providers(cfg, {"gemini-flash-lite"})
    assert [p.model for p in provs] == ["some-flash-lite"] and provs[0].price_in == 0.10


def test_script_report_stage_writes_summary_markdown_and_review_sheet(tmp_path):
    from dataclasses import asdict
    mod = load_script()
    rows, provs = all_rows()
    (tmp_path / "rows.jsonl").write_text("".join(json.dumps(asdict(r)) + "\n" for r in rows))
    (tmp_path / "providers.json").write_text(json.dumps(
        {n: {"model": p.model, "base_url": p.base_url, "price_in": p.price_in, "price_out": p.price_out}
         for n, p in provs.items()}))

    class A:
        results, write = str(tmp_path), str(tmp_path / "BENCH.md")
    assert mod.cmd_report(A) == 0
    summ = json.loads((tmp_path / "summary.json").read_text())
    assert summ["recommendation"]["primary"] and summ["meta"]["pages"] == 2
    assert (tmp_path / "review_sheet.csv").read_text().startswith("model,org") and "**Primary:**" in (tmp_path / "BENCH.md").read_text()


def test_script_run_stage_refuses_to_run_without_keys(tmp_path, monkeypatch):
    mod = load_script()
    for k in ("NVIDIA_API_KEY", "GEMINI_API_KEY"):
        monkeypatch.delenv(k, raising=False)

    class A:
        corpus, models, only, repeats, out = str(tmp_path), str(__import__("pathlib").Path(__file__).parents[1] / "bench" / "models.json"), "", 1, str(tmp_path / "o")
    assert mod.cmd_run(A) == 1
