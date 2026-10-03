from __future__ import annotations

import os
from dataclasses import dataclass


def _int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    request_budget_total: int = 2000
    request_budget_per_company: int = 15
    wall_clock_seconds: int = 2700
    max_workers: int = 8
    bulk_threshold: int = 300  # use bulk roles/subunits snapshots from this many companies upward
    cutoff_margin_seconds: int = 90  # stop starting work this long before the hard limit

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            request_budget_total=_int("REQUEST_BUDGET_TOTAL", 2000),
            request_budget_per_company=_int("REQUEST_BUDGET_PER_COMPANY", 15),
            wall_clock_seconds=_int("WALL_CLOCK_SECONDS", 2700),
            max_workers=_int("MAX_WORKERS", 8),
            bulk_threshold=_int("BULK_THRESHOLD", 300),
            cutoff_margin_seconds=_int("CUTOFF_MARGIN_SECONDS", 90),
        )
