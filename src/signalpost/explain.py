"""Plain-language profile note (2-4 sentences), built deterministically from the envelope's own claims.

Every number and name in the note is copied from a claim; nothing is inferred. It states where facts come from,
confidence, register-vs-website conflicts, changes since the last run and what was not collected.
"""
from __future__ import annotations

import re

from .models import Claim, Envelope

NOT_COLLECTED = "hiring and dated public activity were not collected (they need a verified company website)"
SITE_ONLY = "hiring and activity come only from the company's own site (no job boards, news search or social platforms)"


def _money(v: dict) -> str:
    amount = v["amount"]
    text = f"{amount:,.0f}".replace(",", " ") if float(amount).is_integer() else f"{amount:,.2f}".replace(",", " ")
    return f"{text} {v.get('currency') or ''}".strip()


def _digits(s: str) -> str:
    return re.sub(r"\D", "", s or "")[-8:]


def explain(env: Envelope, had_previous: bool = False) -> str:
    c: dict[str, Claim] = {x.field: x for x in env.claims}

    def val(f: str):
        x = c.get(f)
        return x.value if x and x.availability == "available" else None

    def day(claim: Claim) -> str:
        ev = next((e for e in env.evidence if claim.evidence_ids and e.id == claim.evidence_ids[0]), None)
        return ev.retrieved_at[:10] if ev else "unknown date"

    name = val("legal_name")
    # 1. identity
    if name:
        form = (val("legal_form") or {}).get("description") or (val("legal_form") or {}).get("code")
        addr = val("registered_address") or {}
        place = addr.get("city") or addr.get("municipality") or (val("municipality") or {}).get("name")
        nace = val("nace") or {}
        status = val("status")
        s1 = f"{name}" + (f" ({form})" if form else "") + f", organisation number {env.organisation_number}"
        s1 += f", is {'registered as ' + status if status and status != 'active' else 'an active entity'}"
        s1 += f" in {place.title()}" if place else ""
        s1 += f" operating in {nace['description'].lower()} (NACE {nace['code']})" if nace.get("description") else ""
        src = c["legal_name"]
        s1 += f", per the Brønnøysund register (confidence {src.confidence:.2f}, retrieved {day(src)})."
    elif "registry_record" in c and c["registry_record"].availability == "not_available":
        s1 = (f"Organisation number {env.organisation_number} was not found or has been deleted in the "
              "Brønnøysund register, so no company facts are published.")
    else:
        s1 = (f"No register facts could be retrieved for organisation number {env.organisation_number} in this run"
              " (see errors).")
    # 2. financials
    rev, res, eq = (val(f"financials.{k}") for k in ("revenue", "annual_result", "equity"))
    anchor = c.get("financials.revenue") or c.get("financials.annual_result") or c.get("financials.total_assets")
    if anchor:
        bits = [f"revenue {_money(rev)}" if rev else None, f"annual result {_money(res)}" if res else None,
                f"equity {_money(eq)}" if eq else None]
        bits = [b for b in bits if b] or [f"total assets {_money(val('financials.total_assets'))}"]
        s2 = f"Latest filed accounts ({anchor.reporting_period}): {', '.join(bits)} (Regnskapsregisteret)."
    elif "financials" in c and c["financials"].availability == "failed":
        s2 = "Annual accounts could not be retrieved in this run, so financial figures are unknown."
    else:
        s2 = "The register returned no annual accounts for this entity; financial figures are unknown, not zero."
    # 3. website
    web = c.get("official_website")
    site_phone, reg_phone = val("contact_phone_1"), val("phone") or val("mobile")
    if web and web.availability == "available":
        ev = next((e for e in env.evidence if e.id == web.evidence_ids[0]), None)
        how = (ev.extraction_method or "").split(":")[-1].replace("+", " + ").replace("_", " ") if ev else "identity gate"
        s3 = f"The website {web.value} was verified as belonging to this company ({how}; confidence {web.confidence:.2f})"
        desc = val("website_description")
        s3 += f" and describes the business as “{desc[:160].rstrip()}”." if desc else "."
        if site_phone and reg_phone and _digits(site_phone) != _digits(reg_phone):
            s3 += f" Conflict: the phone number on the site ({site_phone}) differs from the register ({reg_phone})."
        jobs, act = val("open_positions"), val("public_activity")
        if jobs:
            s3 += f" Its careers page lists {len(jobs)} open position(s), e.g. \u201c{jobs[0]['title'][:70]}\u201d."
        elif val("hiring_status") == "no_open_positions":
            s3 += " Its careers page states there are no open positions."
        elif "open_positions" in c:
            s3 += f" No open positions were recognised ({c['open_positions'].note})."
        if act:
            s3 += f" Latest dated item on its site: \u201c{act[0]['title'][:70]}\u201d ({act[0]['date']})."
        elif "public_activity" in c:
            s3 += " No dated public activity was recognised on the site."
    elif web and web.availability == "ambiguous":
        s3 = f"The registered website was not used because its identity could not be confirmed ({web.note})."
    elif web and web.availability in ("blocked", "failed"):
        s3 = f"The registered website could not be read ({web.availability}: {web.note}); no web facts are published."
    elif web:
        s3 = "No usable website: " + (web.note or "none listed") + "."
    else:
        s3 = "Website was not checked in this run."
    # 4. changes / unknowns
    material = [ch for ch in env.changes if ch.get("material")]
    if env.changes:
        parts = [f"{ch['field'].replace('_', ' ')} ({ch['change_type'].replace('_', ' ')})" for ch in material[:3]]
        s4 = (f"Since the previous run {len(env.changes)} change(s) were detected"
              + (f", material: {', '.join(parts)}" if parts else "") + "; ")
    elif had_previous:
        s4 = "No changes since the previous run; "
    else:
        s4 = "First observation of this company; "
    carried = [x.field for x in env.claims if x.carried_forward]
    if carried:
        s4 += f"{len(carried)} fact(s) were kept from an earlier run because their source failed this time; "
    s4 += (SITE_ONLY if web and web.availability == "available" else NOT_COLLECTED) + "."
    return f"{s1} {s2} {s3} {s4}"
