"""Seeded samplers. Never calls external APIs.

    python -m signalpost.sample --universe data/orgs.json --out samples/ --seed 20261003

Writes three DISJOINT sets: submission (>=1500), daily (100, mimics the daily test) and dev (stratified).
Output rows are JSONL: {"organisation_number", "sample_slice", ...register hints}.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

from .universe import load_universe

DEFAULT_SEED = 20261003

# name -> predicate over a universe row. The pool is active filers only, so bankrupt/dissolved
# rows cannot be drawn (checked: 0 of 411,160); that case is covered by fixtures instead.
DEV_STRATA: dict[str, Any] = {
    "large_100plus_employees": lambda r: (r["employees"] or 0) >= 100,
    "mid_20_99_employees": lambda r: 20 <= (r["employees"] or 0) < 100,
    "sole_proprietorship_ENK": lambda r: r["legal_form"] == "ENK",
    "public_limited_ASA": lambda r: r["legal_form"] == "ASA",
    "foreign_branch_NUF": lambda r: r["legal_form"] == "NUF",
    "association_foundation": lambda r: r["legal_form"] in {"FLI", "STI", "VPFO"},
    "housing_coop_BRL_ESEK": lambda r: r["legal_form"] in {"BRL", "ESEK"},
    # NACE 00.000 = industry not specified: 46,537 rows, the best available proxy for dormant shells.
    "dormant_proxy_nace_unspecified": lambda r: r["industry_code"] == "00.000" and not r["employees"] and not r["website"],
    "holding_company_64_2": lambda r: r["industry_code"].startswith("64.2"),
    "with_website": lambda r: bool(r["website"]),
    "no_website_small_AS": lambda r: r["legal_form"] == "AS" and not r["website"] and not r["employees"],
}


def _slim(row: dict[str, Any], sample_slice: str) -> dict[str, Any]:
    return {"organisation_number": row["organisation_number"], "sample_slice": sample_slice}


def build_samples(
    rows: list[dict[str, Any]], seed: int = DEFAULT_SEED, submission: int = 1500, daily: int = 100, per_stratum: int = 6
) -> dict[str, list[dict[str, Any]]]:
    """rows must be sorted (load_universe guarantees it). Same seed + same rows => identical output."""
    rng = random.Random(seed)
    order = list(range(len(rows)))
    rng.shuffle(order)
    if submission + daily > len(rows):
        raise ValueError("universe too small for requested samples")
    daily_rows = [rows[i] for i in order[:daily]]
    submission_rows = [rows[i] for i in order[daily : daily + submission]]
    taken = {r["organisation_number"] for r in daily_rows} | {r["organisation_number"] for r in submission_rows}

    dev: list[dict[str, Any]] = []
    dev_rng = random.Random(seed + 1)
    for name, predicate in DEV_STRATA.items():
        pool = [r for r in rows if r["organisation_number"] not in taken and predicate(r)]
        pick = dev_rng.sample(pool, min(per_stratum, len(pool)))
        for r in sorted(pick, key=lambda r: r["organisation_number"]):
            dev.append(_slim(r, name))
            taken.add(r["organisation_number"])
    return {
        "submission": [_slim(r, "submission") for r in submission_rows],
        "daily": [_slim(r, "daily") for r in daily_rows],
        "dev": dev,
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--universe", default="data/orgs.json")
    parser.add_argument("--out", default="samples")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--submission", type=int, default=1500)
    args = parser.parse_args()
    rows, report = load_universe(args.universe)
    print(f"universe: {report.total_rows} rows, {report.invalid_mod11} invalid mod-11, "
          f"{report.duplicates} duplicates, {report.kept} kept")
    sets = build_samples(rows, args.seed, submission=args.submission)
    for name, items in sets.items():
        write_jsonl(Path(args.out) / f"{name}.jsonl", items)
        print(f"wrote {len(items)} -> {Path(args.out) / (name + '.jsonl')}")
    counts: dict[str, int] = {}
    for item in sets["dev"]:
        counts[item["sample_slice"]] = counts.get(item["sample_slice"], 0) + 1
    print("dev strata:", json.dumps(counts))


if __name__ == "__main__":
    main()
