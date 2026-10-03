"""Automated wrong-company audit of finished envelopes + human review sheet.

HARD flags (a profile with any of them must not be published):
  web_facts_without_verified_identity  web-sourced facts exist but the official website is not verified
  low_identity_confidence              official website published with identity confidence < threshold
  web_source_domain_mismatch           a web fact's evidence comes from a different registered domain
  register_evidence_for_other_org      a register fact's source URL names another organisation number
  financial_not_from_official_api      a financial value whose evidence is not the official accounts API
SOFT flags (review): foreign_org_number_in_web_snippet, website_claims_without_snippet_support,
  legal_name_differs_from_universe     the current register name differs from the (older) frozen universe row. The
                                       record is keyed by the organisation number and its own number was verified, so
                                       this is a rename since the snapshot (seen live: 3 of 1,500), not a wrong company.
"""
from __future__ import annotations

import csv
import io
import json
import random
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .universe import valid_orgnr
from .web.fetch import registered_domain
from .web.identity import PUBLISH_THRESHOLD

WEB = "company_owned_website"
ORG_IN_TEXT = re.compile(r"(?<!\d)(\d{3})[ .\u00a0]?(\d{3})[ .\u00a0]?(\d{3})(?!\d)")
ORG_IN_URL = re.compile(r"/enheter/(\d{9})|overordnetEnhet=(\d{9})|/regnskap/(\d{9})|/regnskap/aarsregnskap/kopi/(\d{9})")
HARD = {"web_facts_without_verified_identity", "low_identity_confidence", "web_source_domain_mismatch",
        "register_evidence_for_other_org", "financial_not_from_official_api"}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").casefold()).strip()


def audit_envelope(env: dict[str, Any], universe_name: str | None = None,
                   threshold: float = PUBLISH_THRESHOLD) -> list[dict[str, str]]:
    org = env.get("organisation_number", "")
    ev = {e["id"]: e for e in env.get("evidence", [])}
    claims = env.get("claims", [])
    flags: list[dict[str, str]] = []

    def flag(kind: str, detail: str) -> None:
        flags.append({"org": org, "flag": kind, "severity": "hard" if kind in HARD else "soft", "detail": detail})

    def first_ev(c: dict[str, Any]) -> dict[str, Any]:
        return ev.get((c.get("evidence_ids") or [None])[0]) or {}

    web = [c for c in claims if c.get("availability") == "available" and first_ev(c).get("source_class") == WEB]
    site = next((c for c in claims if c["field"] == "official_website"), None)
    site_ok = bool(site and site.get("availability") == "available")
    facts = [c for c in web if c["field"] != "official_website"]
    if (facts or (web and not site_ok)) and not site_ok:
        flag("web_facts_without_verified_identity", f"{len(web)} web fact(s) but official_website is "
             f"{site.get('availability') if site else 'absent'}")
    if site_ok and (site.get("confidence") or 0) < threshold:
        flag("low_identity_confidence", f"official_website confidence {site.get('confidence')} < {threshold}")
    if site_ok:
        home = registered_domain(str(site.get("value")))
        for c in facts:
            for eid in c.get("evidence_ids") or []:  # list claims (jobs, news) carry one evidence per item
                dom = registered_domain((ev.get(eid) or {}).get("source_url", ""))
                if dom and home and dom != home:
                    flag("web_source_domain_mismatch", f"{c['field']} from {dom}, official site is {home}")
                    break
    for c in claims:
        e = first_ev(c)
        url = e.get("source_url", "")
        if e.get("source_class", "").startswith("official_") and not url.startswith("https://builderr.ai"):
            m = ORG_IN_URL.search(url)
            found = next((g for g in m.groups() if g), None) if m else None
            if found and found != org:
                flag("register_evidence_for_other_org", f"{c['field']} evidence names {found}")
        if c["field"].startswith(("financials.", "financials_consolidated.")) and c.get("availability") == "available" \
                and e.get("source_class") != "official_annual_accounts":
            flag("financial_not_from_official_api", f"{c['field']} source_class={e.get('source_class')}")
    name = next((c["value"] for c in claims if c["field"] == "legal_name" and c.get("availability") == "available"), None)
    if universe_name and name and _norm(name) != _norm(universe_name):
        flag("legal_name_differs_from_universe", f"{name!r} vs {universe_name!r}")
    for c in facts:
        snippet = first_ev(c).get("claim_span") or ""
        for m in ORG_IN_TEXT.finditer(snippet):
            d = "".join(m.groups())
            if valid_orgnr(d) and d != org:
                flag("foreign_org_number_in_web_snippet", f"{c['field']}: {d}")
        if c["field"] in ("website_description", "contact_email_1", "contact_phone_1") \
                and str(c.get("value", "")).casefold() not in snippet.casefold():
            flag("website_claims_without_snippet_support", c["field"])
    return flags


def audit_file(path: str | Path, universe: dict[str, str] | None = None) -> dict[str, Any]:
    flags: list[dict[str, str]] = []
    n = with_web = 0
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        env = json.loads(ln)
        n += 1
        with_web += any(c["field"] == "official_website" and c.get("availability") == "available"
                        for c in env["claims"])
        flags += audit_envelope(env, (universe or {}).get(env["organisation_number"]))
    hard = [f for f in flags if f["severity"] == "hard"]
    by: dict[str, int] = {}
    for f in flags:
        by[f["flag"]] = by.get(f["flag"], 0) + 1
    return {"profiles": n, "profiles_with_verified_website": with_web, "flags": flags, "hard_flags": len(hard),
            "soft_flags": len(flags) - len(hard), "by_flag": by, "passed": not hard}


# ---------- human review sheet ----------
REGISTER_FIELDS = ("legal_name", "legal_form", "status", "registered_address", "nace", "employees", "founded",
                   "roles", "workplaces", "financials.revenue", "financials.total_assets")


def pick_profiles(envs: list[dict[str, Any]], k: int = 50, seed: int = 20261003) -> list[dict[str, Any]]:
    """Seeded random pick. Profiles carrying web facts are the wrong-company risk, so up to half the sample is
    drawn from them first (when that many exist); the rest is uniform random from the remainder."""
    rng = random.Random(seed)
    risky = [e for e in envs if any(c["field"] == "official_website" and c.get("availability") == "available"
                                    for c in e["claims"])]
    rest = [e for e in envs if e not in risky]
    take_risky = min(len(risky), k // 2)
    chosen = rng.sample(risky, take_risky) + rng.sample(rest, min(len(rest), k - take_risky))
    if len(chosen) < k:  # not enough "rest": top up from the remaining risky ones
        left = [e for e in risky if e not in chosen]
        chosen += rng.sample(left, min(len(left), k - len(chosen)))
    return sorted(chosen, key=lambda e: e["organisation_number"])


def _value(v: Any) -> str:
    if isinstance(v, list):
        return "; ".join(_value(x) for x in v[:6]) + (f" (+{len(v) - 6} more)" if len(v) > 6 else "")
    if isinstance(v, dict):
        return ", ".join(f"{k}={_value(x)}" for k, x in v.items() if x not in (None, ""))
    return str(v)


def sheet_rows(env: dict[str, Any]) -> list[dict[str, str]]:
    ev = {e["id"]: e for e in env["evidence"]}
    name = next((c["value"] for c in env["claims"] if c["field"] == "legal_name" and c["availability"] == "available"),
                "(no register name)")
    rows = []
    for c in env["claims"]:
        e = ev.get((c.get("evidence_ids") or [None])[0]) or {}
        is_web = e.get("source_class") == WEB or c["field"] in ("official_website",) or c["field"].startswith(
            ("website_", "contact_", "social_", "products_"))
        if not (is_web or c["field"] in REGISTER_FIELDS):
            continue
        rows.append({"company": name, "org": env["organisation_number"],
                     "layer": "WEB" if is_web else "REGISTER", "field": c["field"],
                     "availability": c["availability"], "value": _value(c.get("value")) if c.get("value") is not None
                     else (c.get("note") or ""), "confidence": str(c.get("confidence", "")),
                     "source_url": e.get("source_url", ""), "retrieved_at": e.get("retrieved_at", ""),
                     "evidence_snippet": (e.get("claim_span") or "")[:300],
                     "verdict (ok / wrong company / wrong value / unsupported)": ""})
    return rows


def render_sheet(envs: list[dict[str, Any]], flags_by_org: dict[str, list[dict[str, str]]]) -> tuple[str, str]:
    """(markdown, csv). Markdown groups by company and links each org to the register for one-click checking."""
    md = [
        "# Audit review sheet", "",
        ("For each company check: (1) the REGISTER rows against the linked Brønnøysund record, (2) every WEB row: "
         "does the source URL really belong to this company, and does the snippet contain the value? Mark a verdict "
         "per row (CSV has a verdict column). A single 'wrong company' verdict blocks publication of that profile."), ""]
    allrows: list[dict[str, str]] = []
    for env in envs:
        org = env["organisation_number"]
        rows = sheet_rows(env)
        allrows += rows
        name = rows[0]["company"] if rows else "(unknown)"
        reg = f"https://data.brreg.no/enhetsregisteret/api/enheter/{org}"
        md += [f"## {name} — {org}", "", f"Register record: <{reg}>"]
        fl = flags_by_org.get(org, [])
        md += [f"- **{f['severity'].upper()} flag** `{f['flag']}`: {f['detail']}" for f in fl]
        md += ["", "| layer | field | value | confidence | source | snippet |", "|---|---|---|---|---|---|"]
        for r in rows:
            esc = lambda t: t.replace("|", "\\|").replace("\n", " ")
            md.append(f"| {r['layer']} | {r['field']} | {esc(r['value'])[:160]} | {r['confidence']} | "
                      f"{esc(r['source_url'])} | {esc(r['evidence_snippet'])[:160]} |")
        md.append("")
    buf = io.StringIO()
    if allrows:
        w = csv.DictWriter(buf, fieldnames=list(allrows[0]))
        w.writeheader()
        w.writerows(allrows)
    return "\n".join(md) + "\n", buf.getvalue()


def load_envelopes(path: str | Path) -> list[dict[str, Any]]:
    return [json.loads(ln) for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip()]


def universe_names(path: str | Path, wanted: Iterable[str]) -> dict[str, str]:
    from .universe import iter_rows
    want = set(wanted)
    out: dict[str, str] = {}
    if not Path(path).exists():
        return out
    for r in iter_rows(path):
        if r["organisation_number"] in want:
            out[r["organisation_number"]] = r["name"]
            if len(out) == len(want):
                break
    return out


def domain_of(url: str) -> str:
    return urlparse(url).hostname or ""
