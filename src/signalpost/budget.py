"""Thread-safe request budget: global total, per-company cap and a hard wall-clock deadline.

After the deadline (or `expire()`, e.g. on SIGTERM) every `take()` is refused instantly, so in-flight workers
finish within one network timeout and no new outbound request starts.
"""
from __future__ import annotations

import threading
import time
from collections import Counter


class Budget:
    def __init__(self, total: int = 2000, per_company: int = 15, *, deadline: float | None = None,
                 clock=time.monotonic):
        self.total, self.per_company = total, per_company
        self.deadline, self._clock = deadline, clock  # absolute value on `clock`
        self._used = 0
        self._by_org: Counter[str] = Counter()
        self._expired = False
        self._lock = threading.Lock()

    def expire(self) -> None:
        self._expired = True

    @property
    def expired(self) -> bool:
        return self._expired or (self.deadline is not None and self._clock() >= self.deadline)

    def take(self, org: str) -> bool:
        with self._lock:
            if self.expired or self._used >= self.total or self._by_org[org] >= self.per_company:
                return False
            self._used += 1
            self._by_org[org] += 1
            return True

    @property
    def used(self) -> int:
        return self._used

    @property
    def remaining_total(self) -> int:
        return max(0, self.total - self._used)

    def used_by(self, org: str) -> int:
        return self._by_org[org]

    def remaining(self, org: str) -> int:
        with self._lock:
            return max(0, min(self.total - self._used, self.per_company - self._by_org[org]))

    def seconds_left(self) -> float | None:
        return None if self.deadline is None else max(0.0, self.deadline - self._clock())
