#!/usr/bin/env python3
"""Summarise how the web layer behaved on a REAL-website run: identity-gate outcomes, what was extracted (description,
contacts, socials, careers, jobs, news), dropped facts, requests, and concrete samples for manual inspection.

    uv run python scripts/web_report.py --profiles out/web150/envelopes.jsonl --out out/web150/web_report.md
"""
import argparse
import collections
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profiles", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--samples", type=int, default=15)
    a = ap.parse_args()
    envs = [json.loads(ln) for ln in Path(a.profiles).read_text(encoding="utf-8").splitlines() if ln.strip()]
    L: list[str] = []
    p = L.append

    def claims(e):
        return {c["field"]: c for c in e["claims"]}

    def ev(e, c):
        m = {x["id"]: x for x in e["evidence"]}
        return [m[i] for i in c.get("evidence_ids", []) if i in m]
    listed = [e for e in envs if (claims(e).get("registry_website") or {}).get("availability") == "available"]
    p(f"# Real-website run report\n\ncompanies: {len(envs)} | listing a website in the register: {len(listed)}\n")
    states = collections.Counter((claims(e).get("official_website") or {}).get("availability", "absent") for e in listed)
    p(f"## official_website outcome (of {len(listed)} listing a site)\n" + "\n".join(f"- {k}: {v}" for k, v in states.most_common()))
    notes = collections.Counter()
    for e in listed:
        c = claims(e).get("official_website") or {}
        if c.get("availability") != "available":
            n = (c.get("note") or "")
            n = n.split("(signals")[0].split(":")[0] if n.startswith("not published") else n
            notes[f"{c.get('availability')}: {n[:90]}"] += 1
    p("\n## why not verified (top reasons)\n" + "\n".join(f"- {v} x {k}" for k, v in notes.most_common(12)))
    verified = [e for e in listed if (claims(e).get("official_website") or {}).get("availability") == "available"]
    sig = collections.Counter()
    for e in verified:
        for x in ev(e, claims(e)["official_website"]):
            sig[(x.get("extraction_method") or "").replace("identity_gate:", "")] += 1
    p(f"\n## identity signals of the {len(verified)} verified sites\n" + "\n".join(f"- {k}: {v}" for k, v in sig.most_common()))
    fields = ["website_description", "contact_email_1", "contact_phone_1", "social_linkedin", "social_facebook",
              "social_instagram", "products_services", "careers_page", "open_positions", "hiring_status",
              "public_activity", "latest_activity_date"]
    p(f"\n## coverage among the {len(verified)} verified sites")
    for f in fields:
        n = sum(1 for e in verified if (claims(e).get(f) or {}).get("availability") == "available")
        p(f"- {f}: {n}")
    for f in ("open_positions", "public_activity", "careers_page"):
        st = collections.Counter((claims(e).get(f) or {}).get("availability", "absent") for e in verified)
        p(f"- {f} states: {dict(st)}")
    hs = collections.Counter((claims(e).get("hiring_status") or {}).get("value") for e in verified if "hiring_status" in claims(e))
    p(f"- hiring_status values: {dict(hs)}")
    drops = collections.Counter()
    for e in envs:
        for x in e.get("errors", []):
            if x.get("kind") == "dropped_fact":
                drops[f"{x.get('field')}: {x.get('reason')}"] += 1
    p("\n## facts dropped by the verifier / guards\n" + ("\n".join(f"- {v} x {k}" for k, v in drops.most_common(15)) or "- none"))
    reqs = [e["operations"]["requests"] for e in verified]
    allr = [e["operations"]["requests"] for e in listed]
    p(f"\n## requests\n- website-listing companies: mean {sum(allr)/max(len(allr),1):.1f}, max {max(allr or [0])}; verified: mean {sum(reqs)/max(len(reqs),1):.1f}")
    p("\n## samples to inspect by hand (verified sites)")
    for e in verified[: a.samples]:
        c = claims(e)
        name = (c.get("legal_name") or {}).get("value")
        x = ev(e, c["official_website"])[0]
        p(f"\n### {name} ({e['organisation_number']}) -> {c['official_website']['value']}\n- identity: {x.get('extraction_method')} | snippet: {x.get('claim_span')!r}")
        for f in ("website_description", "contact_email_1", "contact_phone_1", "careers_page", "hiring_status", "latest_activity_date"):
            if f in c and c[f].get("availability") == "available":
                p(f"- {f}: {json.dumps(c[f]['value'], ensure_ascii=False)[:160]}")
        for f in ("open_positions", "public_activity"):
            if f in c and c[f].get("availability") == "available":
                for it, evd in zip(c[f]["value"][:4], ev(e, c[f])[:4], strict=False):
                    p(f"- {f}: {it.get('title')!r} {it.get('date') or ''} <{evd.get('source_url')}> snippet: {evd.get('claim_span', '')[:140]!r}")
    for e in listed:
        c = claims(e).get("official_website") or {}
        if c.get("availability") == "ambiguous":
            p(f"\n(ambiguous) {(claims(e).get('legal_name') or {}).get('value')} {e['organisation_number']}: {c.get('note', '')[:200]}")
    text = "\n".join(L) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
