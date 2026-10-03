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
    for rec in sorted(records, key=lambda r: ((r.get("regnskapsperiode") or {}).get("tilDato") or ""), reverse=True):
        kind = str(rec.get("regnskapstype") or "SELSKAP").upper()
        prefix = "financials_consolidated" if kind == "KONSERN" else "financials"
        period = rec.get("regnskapsperiode") or {}
        start, end = period.get("fraDato"), period.get("tilDato")
        if not end:  # a figure without a reporting period is not publishable
            continue
        reporting = f"{start}/{end}" if start else f"/{end}"
        currency = rec.get("valuta")
        for name, path in FIELDS.items():
            raw = _dig(rec, path)
            num = _number(raw)
            if num is None:
                continue
            field = f"{prefix}.{name}"
            if any(c.field == field for c in cs.claims):
                continue  # only the latest period per field; history handled via filing years
            cs.available(field, {"amount": num, "currency": currency}, confidence=CONF_ACC,
                         source_url=url, source_class=SRC, retrieved_at=f.retrieved_at, sha256=f.sha256,
                         span=f"{'.'.join(path)}={num}", method="regnskapsregisteret_json_number",
                         reporting_period=reporting, as_of=end)
            emitted += 1
    if not emitted:
        cs.unavailable("financials", "not_available", note="accounts present but no numeric headline fields",
                       source_url=url, source_class=SRC, retrieved_at=f.retrieved_at, sha256=f.sha256)


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
