"""Polite page fetcher: robots.txt, per-domain throttle, timeouts, bounded retries, byte cap, budget.

At most 1 robots.txt + 1 homepage + N secondary pages per company; every attempt consumes request budget.
"""
from __future__ import annotations

import hashlib
import threading
import time
import urllib.parse
import urllib.robotparser
from dataclasses import dataclass, field

import httpx
import tldextract

from ..budget import Budget
from ..httpcache import utc_now
from .safe import UnsafeUrl, check_public_url

UA_TOKEN = "signalpost-agent"
USER_AGENT = f"{UA_TOKEN}/0.1 (Builderr hackathon entry; respects robots.txt)"
MAX_BYTES = 1_000_000
_EXTRACT = tldextract.TLDExtract(suffix_list_urls=())  # offline: bundled snapshot only, no network call


def registered_domain(url: str) -> str:
    return _EXTRACT(urllib.parse.urlparse(url).hostname or "").top_domain_under_public_suffix


@dataclass
class Page:
    url: str
    final_url: str = ""
    status: int = 0  # 0 = transport failure, -1 = budget exhausted, -2 = blocked (robots/unsafe)
    html: str = ""
    sha256: str | None = None
    retrieved_at: str = ""
    error: str | None = None
    requests: int = 0
    redirected_offsite: bool = False
    extra: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status == 200 and bool(self.html)


class WebFetcher:
    def __init__(self, budget: Budget, *, transport: httpx.BaseTransport | None = None, resolver=None,
                 min_interval: float = 1.0, timeout: float = 10.0, clock=time.monotonic, sleeper=time.sleep):
        self.budget, self.min_interval, self.clock, self.sleeper = budget, min_interval, clock, sleeper
        self._resolver = resolver
        self._http = httpx.Client(transport=transport, timeout=timeout, follow_redirects=False,
                                  headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
        self._last: dict[str, float] = {}
        self._robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self._lock = threading.Lock()

    def _throttle(self, host: str) -> None:
        with self._lock:
            wait = self.min_interval - (self.clock() - self._last.get(host, -1e9))
            self._last[host] = self.clock() + max(wait, 0)
        if wait > 0:
            self.sleeper(wait)

    def _safe(self, url: str) -> None:
        if self._resolver is None:
            check_public_url(url)
        else:
            check_public_url(url, self._resolver)

    def _get(self, url: str, org: str, hops: int = 3) -> tuple[httpx.Response | None, str, int, str | None]:
        """GET with manual, re-validated redirects. Returns (response, final_url, requests_used, error)."""
        used = 0
        for _ in range(hops + 1):
            try:
                self._safe(url)
            except UnsafeUrl as exc:
                return None, url, used, f"unsafe_url: {exc}"
            if not self.budget.take(org):
                return None, url, used, "budget_exhausted"
            used += 1
            self._throttle(urllib.parse.urlparse(url).netloc)
            try:
                resp = self._http.get(url)
            except httpx.HTTPError as exc:
                return None, url, used, type(exc).__name__
            if resp.status_code in (301, 302, 303, 307, 308) and resp.headers.get("location"):
                url = urllib.parse.urljoin(url, resp.headers["location"])
                continue
            return resp, url, used, None
        return None, url, used, "too_many_redirects"

    def robots_allows(self, url: str, org: str) -> tuple[bool | None, int]:
        """(allowed, requests). allowed=None means robots.txt was unreachable (callers go homepage-only)."""
        p = urllib.parse.urlparse(url)
        host = p.netloc.lower()
        if host in self._robots:
            rp = self._robots[host]
            return (None if rp is None else rp.can_fetch(UA_TOKEN, url)), 0
        resp, _, used, _err = self._get(f"{p.scheme}://{host}/robots.txt", org)
        if resp is None or resp.status_code >= 500:
            self._robots[host] = None
            return None, used
        rp = urllib.robotparser.RobotFileParser()
        if resp.status_code in (401, 403):
            rp.disallow_all = True
        elif resp.status_code >= 400:
            rp.allow_all = True
        else:
            rp.parse(resp.text[:200_000].splitlines())
        self._robots[host] = rp
        return rp.can_fetch(UA_TOKEN, url), used

    def page(self, url: str, org: str, *, home_domain: str | None = None) -> Page:
        resp, final, used, err = self._get(url, org)
        pg = Page(url=url, final_url=final, requests=used, retrieved_at=utc_now())
        if resp is None:
            pg.status = -1 if err == "budget_exhausted" else -2 if (err or "").startswith("unsafe") else 0
            pg.error = err
            return pg
        pg.status = resp.status_code
        ctype = resp.headers.get("content-type", "").lower()
        if resp.status_code != 200:
            pg.error = f"HTTP {resp.status_code}"
        elif "html" not in ctype:
            pg.error, pg.status = f"unsupported content-type {ctype[:40]}", 415
        else:
            raw = resp.content[:MAX_BYTES]
            pg.html = raw.decode(resp.encoding or "utf-8", errors="replace")
            pg.sha256 = hashlib.sha256(raw).hexdigest()
        if home_domain and registered_domain(final) != home_domain:
            pg.redirected_offsite = True
        return pg
