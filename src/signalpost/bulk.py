"""Bulk register snapshots: ONE streamed request replaces one request per company for roles and subunits.

Official open data (NLOD) from Enhetsregisteret:
  roles     GET /enhetsregisteret/api/roller/totalbestand            (gzip JSON array, ~130 MB)
  subunits  GET /enhetsregisteret/api/underenheter/lastned           (Accept: ...underenhet.v2+gzip, ~89 MB)
The stream is decompressed and parsed object by object; only wanted organisations are kept (data minimisation:
everything else, including birth dates, is discarded on the fly). Each kept record is returned as a `Fetched`
shaped exactly like the per-company endpoint response, so the normal claim extractors work unchanged.
"""
from __future__ import annotations

import codecs
import hashlib
import json
import zlib
from collections.abc import Iterable, Iterator
from typing import Any

import httpx

from .budget import Budget
from .httpcache import USER_AGENT, Fetched, utc_now

ROLES_BULK_URL = "https://data.brreg.no/enhetsregisteret/api/roller/totalbestand"
SUBUNITS_BULK_URL = "https://data.brreg.no/enhetsregisteret/api/underenheter/lastned"
SUBUNITS_ACCEPT = "application/vnd.brreg.enhetsregisteret.underenhet.v2+gzip;charset=UTF-8"
BULK_KEY = "__bulk__"


class BulkUnavailable(RuntimeError):
    """The bulk file could not be read completely; callers fall back to per-company requests."""


def iter_json_array_gz(chunks: Iterable[bytes]) -> Iterator[dict[str, Any]]:
    """Yield the objects of a gzip-compressed top-level JSON array without loading it into memory."""
    gz = zlib.decompressobj(16 + zlib.MAX_WBITS)
    text_dec = codecs.getincrementaldecoder("utf-8")(errors="replace")
    dec = json.JSONDecoder()
    buf, closed = "", False
    for chunk in chunks:
        buf += text_dec.decode(gz.decompress(chunk))
        i, n = 0, len(buf)
        while True:
            while i < n and buf[i] in " \n\r\t,[":
                i += 1
            if i >= n:
                break
            if buf[i] == "]":
                closed = True
                break
            try:
                obj, end = dec.raw_decode(buf, i)
            except json.JSONDecodeError:
                break  # object continues in the next chunk
            yield obj
            i = end
        buf = buf[i:]
        if closed:
            return
    buf += text_dec.decode(gz.flush(), final=True)
    if buf.strip(" \n\r\t,]"):
        raise BulkUnavailable("bulk stream ended inside a JSON object (truncated download)")


def _stream(url: str, accept: str, budget: Budget, transport: httpx.BaseTransport | None,
            read_timeout: float) -> Iterator[bytes]:
    if not budget.take(BULK_KEY):
        raise BulkUnavailable("request budget exhausted or deadline passed")
    with httpx.Client(transport=transport, timeout=httpx.Timeout(30.0, read=read_timeout),
                      headers={"User-Agent": USER_AGENT, "Accept": accept}) as client, \
            client.stream("GET", url) as resp:
        if resp.status_code != 200:
            raise BulkUnavailable(f"HTTP {resp.status_code}")
        for chunk in resp.iter_raw(1 << 16):
            if budget.expired:
                raise BulkUnavailable("wall-clock deadline reached during bulk download")
            yield chunk


def _fetched(url: str, body: Any, at: str) -> Fetched:
    sha = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return Fetched(url, 200, body, sha, at, requests=0, via="bulk")


def bulk_roles(wanted: set[str], budget: Budget, *, transport: httpx.BaseTransport | None = None,
               read_timeout: float = 60.0) -> dict[str, Fetched]:
    """org -> Fetched shaped like /enheter/{org}/roller. Orgs absent from the complete snapshot get HTTP 404."""
    found: dict[str, dict[str, Any]] = {}
    try:
        for obj in iter_json_array_gz(_stream(ROLES_BULK_URL, "application/gzip", budget, transport, read_timeout)):
            org = obj.get("organisasjonsnummer")
            if org in wanted:
                found[org] = {"rollegrupper": obj.get("rollegrupper") or []}
    except (httpx.HTTPError, zlib.error) as exc:
        raise BulkUnavailable(type(exc).__name__) from exc
    at = utc_now()
    out: dict[str, Fetched] = {}
    for org in wanted:
        url = f"https://data.brreg.no/enhetsregisteret/api/enheter/{org}/roller"
        out[org] = _fetched(url, found[org], at) if org in found else Fetched(url, 404, None, None, at, error="HTTP 404", via="bulk")
    return out


def bulk_subunits(wanted: set[str], budget: Budget, *, transport: httpx.BaseTransport | None = None,
                  read_timeout: float = 60.0) -> dict[str, Fetched]:
    """org -> Fetched shaped like /underenheter?overordnetEnhet={org}. No subunits => 404 (checked, none)."""
    found: dict[str, list[dict[str, Any]]] = {}
    try:
        for obj in iter_json_array_gz(_stream(SUBUNITS_BULK_URL, SUBUNITS_ACCEPT, budget, transport, read_timeout)):
            parent = obj.get("overordnetEnhet")
            if parent in wanted:
                found.setdefault(parent, []).append(obj)
    except (httpx.HTTPError, zlib.error) as exc:
        raise BulkUnavailable(type(exc).__name__) from exc
    at = utc_now()
    out: dict[str, Fetched] = {}
    for org in wanted:
        url = f"https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet={org}&size=100"
        out[org] = _fetched(url, {"_embedded": {"underenheter": found[org]}}, at) if org in found \
            else Fetched(url, 404, None, None, at, error="HTTP 404", via="bulk")
    return out
