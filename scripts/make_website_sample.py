#!/usr/bin/env python3
"""Seeded random sample of companies that LIST a website in the Brreg bulk CSV (gzip or plain).

    uv run python scripts/make_website_sample.py --csv brreg-enheter.csv.gz --count 150 --out samples/websites150.jsonl
"""
import argparse
import csv
import gzip
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "kit" / "src")]

from signalpost.universe import valid_orgnr


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--count", type=int, default=150)
    ap.add_argument("--seed", type=int, default=20261004)
    ap.add_argument("--out", default=str(ROOT / "samples" / "websites150.jsonl"))
    a = ap.parse_args()
    with open(a.csv, "rb") as probe:
        opener = gzip.open if probe.read(2) == b"\x1f\x8b" else open
    rows = []
    with opener(a.csv, "rt", encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            org = r.get("organisasjonsnummer", "")
            if (r.get("hjemmeside") or "").strip() and valid_orgnr(org) and r.get("konkurs") != "true" \
                    and r.get("underAvvikling") != "true" and r.get("sisteInnsendteAarsregnskap") == "2025":
                rows.append(org)
    rows.sort()
    random.Random(a.seed).shuffle(rows)
    pick = sorted(rows[: a.count])
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("".join(json.dumps({"organisation_number": o, "sample_slice": "website_listed"}) + "\n"
                                   for o in pick), encoding="utf-8")
    print(f"{len(rows)} eligible companies list a website; wrote {len(pick)} to {a.out}")
    return 0 if pick else 1


if __name__ == "__main__":
    raise SystemExit(main())
