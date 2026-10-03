"""Thread-safe request budget: global total and per-company caps."""
from __future__ import annotations

import threading
from collections import Counter


class Budget:
    def __init__(self, total: int = 2000, per_company: int = 15):
        self.total, self.per_company = total, per_company
        self._used = 0
        self._by_org: Counter[str] = Counter()
        self._lock = threading.Lock()

    def take(self, org: str) -> bool:
        with self._lock:
            if self._used >= self.total or self._by_org[org] >= self.per_company:
                return False
            self._used += 1
            self._by_org[org] += 1
            return True

    @property
    def used(self) -> int:
        return self._used

    def used_by(self, org: str) -> int:
        return self._by_org[org]

    def remaining(self, org: str) -> int:
        with self._lock:
            return max(0, min(self.total - self._used, self.per_company - self._by_org[org]))
