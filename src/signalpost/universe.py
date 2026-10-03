"""Streaming loader and validation for the public Signalpost universe (JSONL or JSONL.gz)."""
from __future__ import annotations

import gzip
import json
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_WEIGHTS = (3, 2, 7, 6, 5, 4, 3, 2)


def valid_orgnr(value: str) -> bool:
    """Norwegian organisation number: 9 digits, mod-11 check digit (weights 3,2,7,6,5,4,3,2)."""
    if len(value) != 9 or not value.isascii() or not value.isdigit():
        return False
    remainder = 11 - sum(int(d) * w for d, w in zip(value, _WEIGHTS, strict=False)) % 11
    check = 0 if remainder == 11 else remainder
    return check != 10 and check == int(value[8])


def _open(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8")
    return path.open(encoding="utf-8")


def iter_rows(path: str | Path) -> Iterator[dict[str, Any]]:
    path = Path(path)
    with _open(path) as handle:
        head = handle.read(64)
        if head.startswith("version https://git-lfs"):
            raise RuntimeError(f"{path} is a Git LFS pointer, not data; run `git lfs pull`")
        handle.seek(0)
        for line in handle:
            if line.strip():
                yield json.loads(line)


@dataclass
class LoadReport:
    total_rows: int = 0
    invalid_mod11: int = 0
    duplicates: int = 0
    kept: int = 0
    invalid_examples: list[str] = field(default_factory=list)


def load_universe(path: str | Path) -> tuple[list[dict[str, Any]], LoadReport]:
    """Return valid, de-duplicated rows sorted by organisation number (deterministic order)."""
    report = LoadReport()
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for row in iter_rows(path):
        report.total_rows += 1
        org = str(row.get("organisation_number") or "")
        if not valid_orgnr(org):
            report.invalid_mod11 += 1
            if len(report.invalid_examples) < 5:
                report.invalid_examples.append(org)
            continue
        if org in seen:
            report.duplicates += 1
            continue
        seen.add(org)
        rows.append(row)
    rows.sort(key=lambda r: r["organisation_number"])
    report.kept = len(rows)
    return rows, report
