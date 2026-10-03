"""Official-API client: SQLite cache, ETag revalidation, retries with backoff, request budget.

Every network attempt consumes budget. A 304 revalidation still counts as a request but reuses the body.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from .budget import Budget

SLOW_ENDPOINTS = {"/aarsregnskap/kopi/": 2.1}  # Brreg: ~30 requests/minute on the filing-years endpoint
USER_AGENT = "signalpost-agent/0.1 (Builderr hackathon entry; official-API reads only)"


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


@dataclass
class Fetched:
    url: str
    status: int  # HTTP status; 0 = transport failure; -1 = budget exhausted
    body: Any = None
    sha256: str | None = None
    retrieved_at: str = ""
    error: str | None = None
    from_cache: bool = False
    requests: int = 0

    @property
    def ok(self) -> bool:
        return self.status == 200


class ApiClient:
    def __init__(self, cache_path: str | Path = ":memory:", budget: Budget | None = None,
                 transport: httpx.BaseTransport | None = None, attempts: int = 3, timeout: float = 15.0,
                 sleeper=time.sleep):
        self.budget = budget or Budget()
        self.attempts, self.sleeper = attempts, sleeper
        self._http = httpx.Client(transport=transport, timeout=timeout, follow_redirects=False,
                                  headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        self._db = sqlite3.connect(str(cache_path), check_same_thread=False)
        self._db.execute("CREATE TABLE IF NOT EXISTS http_cache(url TEXT PRIMARY KEY, etag TEXT, status INT, "
                         "body BLOB, sha256 TEXT, fetched_at TEXT)")
        self._lock = threading.Lock()
        self._slow_lock = threading.Lock()
        self._slow_next: dict[str, float] = {}
        self._clock = time.monotonic

    def _pace(self, url: str) -> None:
        for marker, gap in SLOW_ENDPOINTS.items():
            if marker in url:
                with self._slow_lock:
                    start = max(self._clock(), self._slow_next.get(marker, 0.0))
                    self._slow_next[marker] = start + gap
                delay = start - self._clock()
                if delay > 0:
                    self.sleeper(delay)

    def _cached(self, url: str):
        with self._lock:
            return self._db.execute("SELECT etag,status,body,sha256,fetched_at FROM http_cache WHERE url=?", (url,)).fetchone()

    def _store(self, url: str, etag: str | None, status: int, raw: bytes, sha: str, at: str) -> None:
        with self._lock:
            self._db.execute("REPLACE INTO http_cache VALUES(?,?,?,?,?,?)", (url, etag, status, raw, sha, at))
            self._db.commit()

    def get_json(self, url: str, org: str) -> Fetched:
        cached = self._cached(url)
        headers = {"If-None-Match": cached[0]} if cached and cached[0] and cached[1] == 200 else {}
        used = 0
        error = "request failed"
        for attempt in range(self.attempts):
            if not self.budget.take(org):
                return Fetched(url, -1, error="budget_exhausted", retrieved_at=utc_now(), requests=used)
            used += 1
            self._pace(url)
            try:
                resp = self._http.get(url, headers=headers)
            except httpx.HTTPError as exc:
                error = type(exc).__name__
                self.sleeper(0.4 * 2**attempt)
                continue
            at = utc_now()
            if resp.status_code == 304 and cached:
                return Fetched(url, 200, json.loads(cached[2]), cached[3], at, from_cache=True, requests=used)
            if resp.status_code in (404, 410):
                sha = hashlib.sha256(resp.content).hexdigest()
                return Fetched(url, resp.status_code, None, sha, at, error=f"HTTP {resp.status_code}", requests=used)
            if resp.status_code == 200:
                raw = resp.content
                try:
                    body = json.loads(raw)
                except ValueError:
                    return Fetched(url, 200, None, None, at, error="invalid_json", requests=used)
                sha = hashlib.sha256(raw).hexdigest()
                self._store(url, resp.headers.get("etag"), 200, raw, sha, at)
                return Fetched(url, 200, body, sha, at, requests=used)
            error = f"HTTP {resp.status_code}"
            if resp.status_code == 429:
                try:
                    delay = min(float(resp.headers.get("retry-after", "")), 30.0)
                except ValueError:
                    delay = 0.4 * 2**attempt
                self.sleeper(delay)
            elif resp.status_code >= 500:
                self.sleeper(0.4 * 2**attempt)
            else:
                break
        return Fetched(url, 0, None, None, utc_now(), error=error, requests=used)
