"""Outbound URL safety: public http(s) only; no localhost/private/link-local/reserved targets."""
from __future__ import annotations

import ipaddress
import socket
import urllib.parse


class UnsafeUrl(ValueError):
    pass


def check_public_url(url: str, resolver=socket.getaddrinfo) -> str:
    """Return the URL if safe, else raise UnsafeUrl. IP literals and resolved addresses must be global.

    If DNS cannot resolve (e.g. behind an egress proxy) we do not block here; the fetch itself will fail.
    Residual risk: DNS rebinding between this check and the connection (documented in LIMITATIONS).
    """
    p = urllib.parse.urlparse(url)
    host = (p.hostname or "").lower().rstrip(".")
    if p.scheme not in {"http", "https"} or not host:
        raise UnsafeUrl("only http(s) URLs with a host are allowed")
    if p.username or p.password:
        raise UnsafeUrl("credentials in URL are not allowed")
    if host == "localhost" or host.endswith((".localhost", ".local", ".internal")):
        raise UnsafeUrl("local hostnames are blocked")
    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None
    if literal is not None:
        if not literal.is_global:
            raise UnsafeUrl("non-global IP address blocked")
        return url
    try:
        infos = resolver(host, p.port or (443 if p.scheme == "https" else 80), type=socket.SOCK_STREAM)
    except OSError:
        return url
    for info in infos:
        if not ipaddress.ip_address(info[4][0]).is_global:
            raise UnsafeUrl("hostname resolves to a non-global address")
    return url


def normalize_homepage(value: str | None) -> str | None:
    value = str(value or "").strip()
    if not value or " " in value:
        return None
    if not value.lower().startswith(("http://", "https://")):
        value = "https://" + value
    p = urllib.parse.urlparse(value)
    if not p.hostname or "." not in p.hostname:
        return None
    return urllib.parse.urlunparse((p.scheme, p.netloc, p.path or "/", "", "", ""))
