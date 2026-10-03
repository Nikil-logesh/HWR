"""Accounts layer: financial values come ONLY from Regnskapsregisteret JSON numbers. Never from an LLM.

Missing is omitted (never zero); a literal 0 in the filing is preserved.
"""
from __future__ import annotations

from typing import Any

from .claims import ClaimSet
from .httpcache import Fetched

ACCOUNTS_URL = "https://data.brreg.no/regnskapsregisteret/regnskap/{org}"
YEARS_URL = "https://data.brreg.no/regnskapsregisteret/regnskap/aarsregnskap/kopi/{org}/aar"
SRC = "official_annual_accounts"
SRC_YEARS = "official_annual_account_copies"

FIELDS: dict[str, tuple[str, ...]] = {
    "revenue": ("resultatregnskapResultat", "driftsresultat", "driftsinntekter", "sumDriftsinntekter"),
    "operating_result": ("resultatregnskapResultat", "driftsresultat", "driftsresultat"),
    "profit_before_tax": ("resultatregnskapResultat", "ordinaertResultatFoerSkattekostnad"),
    "annual_result": ("resultatregnskapResultat", "aarsresultat"),
    "total_assets": ("eiendeler", "sumEiendeler"),
    "equity": ("egenkapitalGjeld", "egenkapital", "sumEgenkapital"),
    "total_debt": ("egenkapitalGjeld", "gjeldOversikt", "sumGjeld"),
}


def _dig(d: Any, path: tuple[str, ...]) -> Any:
    for k in path:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def _number(v: Any) -> int | float | None:
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def accounts_claims(cs: ClaimSet, org: str, f: Fetched) -> None:
    url = ACCOUNTS_URL.format(org=org)
    if f.status in (404, 410):
        cs.unavailable("financials", "not_available", note=f"HTTP {f.status}: no annual accounts returned (not zero)",
                       source_url=url, source_class=SRC, retrieved_at=f.retrieved_at, sha256=f.sha256)
        return
    if not f.ok:
        cs.unavailable("financials", "failed", note=f"accounts fetch failed: {f.error}")
        return
    records = f.body if isinstance(f.body, list) else []
    records = [r for r in records if isinstance(r, dict)]
    if not records:
        cs.unavailable("financials", "not_available", note="accounts endpoint returned no records",
                       source_url=url, source_class=SRC, retrieved_at=f.retrieved_at, sha256=f.sha256)
        return
    emitted = 0
    by_kind: dict[str, list[dict[str, Any]]] = {}
    for rec in records:
        if (rec.get("regnskapsperiode") or {}).get("tilDato"):  # a figure without a period is not publishable
            by_kind.setdefault(str(rec.get("regnskapstype") or "SELSKAP").upper(), []).append(rec)
    for kind, recs in sorted(by_kind.items()):
        recs.sort(key=lambda r: r["regnskapsperiode"]["tilDato"], reverse=True)
        prefix = "financials_consolidated" if kind == "KONSERN" else "financials"
        latest = recs[0]  # only the latest period: never mix periods under a "latest" field
        reporting, end = _period(latest), latest["regnskapsperiode"]["tilDato"]
        for name, path in FIELDS.items():
            num = _number(_dig(latest, path))
            if num is None:
                continue
            cs.available(f"{prefix}.{name}", {"amount": num, "currency": latest.get("valuta")},
                         confidence=CONF_ACC, source_url=url, source_class=SRC, retrieved_at=f.retrieved_at,
                         sha256=f.sha256, span=f"{'.'.join(path)}={num}", method="regnskapsregisteret_json_number",
                         reporting_period=reporting, as_of=end)
            emitted += 1
        history = []
        for rec in recs:  # same response, zero extra requests
            row = {"reporting_period": _period(rec), "currency": rec.get("valuta")}
            for name, path in FIELDS.items():
                num = _number(_dig(rec, path))
                if num is not None:
                    row[name] = num
            history.append(row)
        if len(history) > 1:
            cs.available(f"{prefix}_history", history, confidence=CONF_ACC, source_url=url, source_class=SRC,
                         retrieved_at=f.retrieved_at, sha256=f.sha256,
                         span="; ".join(f"{h['reporting_period']}" for h in history),
                         method="regnskapsregisteret_json_number")
    if not emitted:
        cs.unavailable("financials", "not_available", note="accounts present but no numeric headline fields",
                       source_url=url, source_class=SRC, retrieved_at=f.retrieved_at, sha256=f.sha256)


def _period(rec: dict[str, Any]) -> str:
    p = rec["regnskapsperiode"]
    return f"{p['fraDato']}/{p['tilDato']}" if p.get("fraDato") else f"/{p['tilDato']}"


CONF_ACC = 0.99


def years_claims(cs: ClaimSet, org: str, f: Fetched) -> None:
    url = YEARS_URL.format(org=org)
    if f.status in (404, 410):
        cs.unavailable("financial_history_years", "not_available", note=f"HTTP {f.status}", source_url=url,
                       source_class=SRC_YEARS, retrieved_at=f.retrieved_at, sha256=f.sha256)
        return
    if not f.ok:
        cs.unavailable("financial_history_years", "failed", note=f"history fetch failed: {f.error}")
        return
    years = sorted({str(y) for y in f.body if str(y).isdigit()}) if isinstance(f.body, list) else []
    if not years:
        cs.unavailable("financial_history_years", "not_available", note="no filing years listed", source_url=url,
                       source_class=SRC_YEARS, retrieved_at=f.retrieved_at, sha256=f.sha256)
        return
    cs.available("financial_history_years", years, confidence=CONF_ACC, source_url=url, source_class=SRC_YEARS,
                 retrieved_at=f.retrieved_at, sha256=f.sha256, span=",".join(years), method="brreg_filing_years")
