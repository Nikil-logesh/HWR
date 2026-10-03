#!/usr/bin/env python3
"""Pick 50 random profiles and write a human-review sheet; also run the automated wrong-company audit.

    uv run python scripts/audit_sample.py --profiles out/profiles.jsonl --out out/audit [--k 50] [--seed N]

Outputs: audit_sheet.md (readable, links to the register), audit_sheet.csv (verdict column), audit_flags.json.
Exit code 1 if any HARD flag exists in the WHOLE file (not just the sample).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "kit" / "src")]

from signalpost import audit


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profiles", default=str(ROOT / "out" / "profiles.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "out" / "audit"))
    ap.add_argument("--k", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20261003)
    ap.add_argument("--universe", default=str(ROOT / "data" / "orgs.json"))
    a = ap.parse_args()
    envs = audit.load_envelopes(a.profiles)
    names = audit.universe_names(a.universe, [e["organisation_number"] for e in envs])
    result = audit.audit_file(a.profiles, names)
    by_org: dict[str, list] = {}
    for f in result["flags"]:
        by_org.setdefault(f["org"], []).append(f)
    chosen = audit.pick_profiles(envs, a.k, a.seed)
    md, csv_text = audit.render_sheet(chosen, by_org)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "audit_sheet.md").write_text(md, encoding="utf-8")
    (out / "audit_sheet.csv").write_text(csv_text, encoding="utf-8")
    (out / "audit_flags.json").write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    web_in_sample = sum(1 for e in chosen if any(c["field"] == "official_website" and c["availability"] == "available"
                                                 for c in e["claims"]))
    print(f"profiles audited: {result['profiles']} | with verified website: {result['profiles_with_verified_website']}")
    print(f"HARD flags: {result['hard_flags']} | soft flags: {result['soft_flags']} | by flag: {result['by_flag']}")
    print(f"review sheet: {len(chosen)} profiles ({web_in_sample} with web facts) -> {out / 'audit_sheet.md'} / .csv")
    print("AUDIT", "PASSED" if result["passed"] else "FAILED (hard flags: do not publish those profiles)")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
