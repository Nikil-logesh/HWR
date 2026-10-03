#!/usr/bin/env python3
"""Benchmark the LLM text-extraction step. Three stages (the first two need network / keys):

  1. corpus  build a frozen corpus of identity-verified company pages  (needs data.brreg.no + company websites)
       uv run python scripts/model_benchmark.py corpus --count 30 --out bench/corpus
  2. run     send the same corpus + injection probes to each model     (needs NVIDIA_API_KEY / GEMINI_API_KEY ...)
       uv run python scripts/model_benchmark.py run --corpus bench/corpus --out bench/results/latest
  3. report  compute metrics, recommendation and BENCHMARK.md from the raw rows (no network)
       uv run python scripts/model_benchmark.py report --results bench/results/latest --write BENCHMARK.md

The corpus holds third-party page text, so bench/corpus/ is git-ignored; only aggregate results are committed.
"""
import argparse
import json
import os
import random
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "kit" / "src")]

from signalpost import modelbench as mb
from signalpost.budget import Budget
from signalpost.claims import ClaimSet
from signalpost.httpcache import ApiClient
from signalpost.register import entity_claims
from signalpost.universe import iter_rows
from signalpost.web.enrich import enrich_website
from signalpost.web.fetch import WebFetcher
from signalpost.web.identity import CompanyIdentity
from signalpost.web.llm import Provider


def load_providers(path: Path, only: set[str] | None) -> tuple[list[Provider], list[str]]:
    cfg = json.loads(path.read_text(encoding="utf-8"))["models"]
    out, skipped = [], []
    for m in cfg:
        if only and m["name"] not in only:
            continue
        key = os.environ.get(m["key_env"], "")
        model = m.get("model") or os.environ.get(m.get("model_env", ""), "")
        if not key or not model:
            skipped.append(f"{m['name']} (missing {m['key_env'] if not key else m.get('model_env')})")
            continue
        out.append(Provider(m["name"], m["base_url"].rstrip("/"), model, key, m.get("price_in", 0.0),
                            m.get("price_out", 0.0), m.get("json_mode", True), m.get("extra_body", {}),
                            m.get("max_tokens", 1000)))
    return out, skipped


def cmd_corpus(a) -> int:
    rows = [r for r in iter_rows(a.universe) if r.get("website")]
    random.Random(a.seed).shuffle(rows)
    budget = Budget(10**6, 10**6)
    client, fetcher = ApiClient(budget=budget), WebFetcher(budget)
    items, stats = [], {"attempted": 0, "verified": 0, "ambiguous": 0, "no_site": 0, "failed_or_blocked": 0}
    for r in rows:
        if len(items) >= a.count or stats["attempted"] >= a.max_attempts:
            break
        stats["attempted"] += 1
        org = r["organisation_number"]
        cs = ClaimSet()
        f = client.get_json(f"https://data.brreg.no/enhetsregisteret/api/enheter/{org}", org)
        if not entity_claims(cs, org, f):
            continue
        c = {x.field: x.value for x in cs.claims if x.availability == "available"}
        addr = c.get("registered_address") or {}
        ident = CompanyIdentity(org, c["legal_name"], addr.get("street"), addr.get("postcode"), addr.get("city"),
                                addr.get("municipality"), c.get("phone"))
        captured = []
        out = enrich_website(ClaimSet(), ident, r["website"], fetcher, None, capture=captured)
        if out.state == "verified":
            stats["verified"] += 1
            items.append(mb.CorpusItem(org, ident.name, "real", [{"url": p.url, "text": p.text, "corpus": p.corpus}
                                                                 for p in captured]))
        else:
            key = {"ambiguous": "ambiguous", "not_available": "no_site"}.get(out.state, "failed_or_blocked")
            stats[key] += 1
        print(f"{org} {ident.name[:40]:<40} {out.state}", file=sys.stderr)
    mb.save_corpus(items, a.out)
    Path(a.out, "_corpus_stats.json").write_text(json.dumps(stats, indent=1))
    print(f"corpus: {len(items)} verified pages saved to {a.out}; identity-gate outcomes on live sites: {stats}")
    return 0 if items else 1


def cmd_run(a) -> int:
    providers, skipped = load_providers(Path(a.models), set(a.only.split(",")) if a.only else None)
    for s in skipped:
        print(f"skipping {s}", file=sys.stderr)
    if not providers:
        print("no model has a key/model id configured; nothing to run", file=sys.stderr)
        return 1
    corpus = mb.load_corpus(a.corpus) + mb.injection_items()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    all_rows = []
    for p in providers:
        for rep in range(a.repeats):
            rows = mb.evaluate_model(p, corpus, progress=lambda m: print(m, file=sys.stderr))
            all_rows += rows
    (out / "rows.jsonl").write_text("".join(json.dumps(asdict(r), ensure_ascii=False) + "\n" for r in all_rows),
                                    encoding="utf-8")
    (out / "providers.json").write_text(json.dumps(
        {p.name: {"model": p.model, "base_url": p.base_url, "price_in": p.price_in, "price_out": p.price_out}
         for p in providers}, indent=1))
    print(f"wrote {len(all_rows)} rows to {out / 'rows.jsonl'}; now run the `report` stage")
    return 0


def cmd_report(a) -> int:
    d = Path(a.results)
    rows = [mb.Row(**json.loads(ln)) for ln in (d / "rows.jsonl").read_text(encoding="utf-8").splitlines() if ln.strip()]
    pj = json.loads((d / "providers.json").read_text())
    providers = {n: Provider(n, v["base_url"], v["model"], "", v["price_in"], v["price_out"]) for n, v in pj.items()}
    summary = mb.summarize(rows, providers)
    rec = mb.recommend(summary)
    first = next(iter(summary.values()), {})
    meta = {"run_at": datetime.fromtimestamp((d / "rows.jsonl").stat().st_mtime, UTC).strftime("%Y-%m-%d %H:%M UTC"),
            "pages": first.get("pages", 0), "injection_probes": first.get("injection_probes", 0)}
    (d / "summary.json").write_text(json.dumps({"summary": summary, "recommendation": rec, "meta": meta}, indent=1,
                                               ensure_ascii=False))
    (d / "review_sheet.csv").write_text(mb.review_sheet(rows), encoding="utf-8")
    md = mb.render_markdown(summary, rec, meta)
    Path(a.write).write_text(md, encoding="utf-8")
    print(md)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("corpus")
    c.add_argument("--count", type=int, default=30)
    c.add_argument("--max-attempts", type=int, default=150)
    c.add_argument("--seed", type=int, default=20261003)
    c.add_argument("--universe", default=str(ROOT / "data" / "orgs.json"))
    c.add_argument("--out", default=str(ROOT / "bench" / "corpus"))
    r = sub.add_parser("run")
    r.add_argument("--corpus", default=str(ROOT / "bench" / "corpus"))
    r.add_argument("--models", default=str(ROOT / "bench" / "models.json"))
    r.add_argument("--only", default="")
    r.add_argument("--repeats", type=int, default=1)
    r.add_argument("--out", default=str(ROOT / "bench" / "results" / "latest"))
    p = sub.add_parser("report")
    p.add_argument("--results", default=str(ROOT / "bench" / "results" / "latest"))
    p.add_argument("--write", default=str(ROOT / "BENCHMARK.md"))
    a = ap.parse_args()
    return {"corpus": cmd_corpus, "run": cmd_run, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
