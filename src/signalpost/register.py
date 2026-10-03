"""Register layer (no LLM): Enhetsregisteret entity, roles, subunits and universe-row fallback -> claims.

Every Brreg field is treated as optional: the code never assumes a key exists and never turns a missing
value into zero/false. Person birth dates are never read.
"""
from __future__ import annotations

import json
from typing import Any

from .claims import ClaimSet
from .httpcache import Fetched, utc_now

ENTITY_URL = "https://data.brreg.no/enhetsregisteret/api/enheter/{org}"
ROLES_URL = ENTITY_URL + "/roller"
SUBUNITS_URL = "https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet={org}&size=100"
UNIVERSE_URL = "https://builderr.ai/signalpost-company-universe-2025.jsonl.gz"
UNIVERSE_SHA = "b82d6a3e7231d1759a958c282bc4366b80ec2fab8095053d8ed7fa9cd01bc838"
LIVE = "official_registry_live"
ROLES = "official_roles"
SUBUNITS = "official_subunits"
BULK = "official_registry_bulk"
CONF = 0.99  # official register record for the exact organisation number


def _g(d: Any, *path: str) -> Any:
    for key in path:
        if not isinstance(d, dict):
            return None
        d = d.get(key)
    return d


def _span(path: str, value: Any) -> str:
    return f"{path}={json.dumps(value, ensure_ascii=False)}"


def _address(a: Any) -> dict[str, Any] | None:
    if not isinstance(a, dict):
        return None
    street = a.get("adresse")
    street = ", ".join(s for s in street if s) if isinstance(street, list) else street
    out = {"street": street or None, "postcode": a.get("postnummer"), "city": a.get("poststed"),
           "municipality": a.get("kommune"), "municipality_number": a.get("kommunenummer"),
           "country": a.get("land")}
    out = {k: v for k, v in out.items() if v not in (None, "")}
    return out or None


def status_of(e: dict[str, Any]) -> tuple[str, str]:
    """Return (status, evidence span). Only flags literally present are quoted."""
    if e.get("slettedato"):
        return "deleted", _span("slettedato", e["slettedato"])
    if e.get("konkurs") is True:
        return "bankrupt", _span("konkurs", True)
    if e.get("underTvangsavviklingEllerTvangsopplosning") is True:
        return "forced_dissolution", _span("underTvangsavviklingEllerTvangsopplosning", True)
    if e.get("underAvvikling") is True:
        return "liquidating", _span("underAvvikling", True)
    flags = {k: e[k] for k in ("konkurs", "underAvvikling", "underTvangsavviklingEllerTvangsopplosning") if k in e}
    return "active", "no insolvency/dissolution flags set: " + json.dumps(flags, sort_keys=True)


def entity_claims(cs: ClaimSet, org: str, f: Fetched) -> bool:
    """Add claims from the live entity record. Returns True if a usable record was read."""
    url = ENTITY_URL.format(org=org)
    if f.status in (404, 410):
        cs.unavailable("registry_record", "not_available", note=f"Brreg returned HTTP {f.status} for {org}: "
                       "entity not found or deleted", source_url=url, source_class=LIVE,
                       retrieved_at=f.retrieved_at, sha256=f.sha256)
        return False
    if not f.ok or not isinstance(f.body, dict):
        cs.unavailable("registry_record", "failed", note=f"live entity fetch failed: {f.error}")
        return False
    e = f.body
    if e.get("organisasjonsnummer") != org:
        cs.unavailable("registry_record", "ambiguous", note="returned record has a different organisation number")
        return False

    def put(field: str, value: Any, span: str, **kw: Any) -> None:
        if value in (None, "", [], {}):
            return
        cs.available(field, value, confidence=CONF, source_url=url, source_class=LIVE,
                     retrieved_at=f.retrieved_at, sha256=f.sha256, span=span,
                     method="brreg_bulk_csv_field" if f.via == "bulk" else "brreg_json_field", **kw)

    put("legal_name", e.get("navn"), _span("navn", e.get("navn")))
    form = _g(e, "organisasjonsform", "kode")
    put("legal_form", {"code": form, "description": _g(e, "organisasjonsform", "beskrivelse")},
        _span("organisasjonsform.kode", form)) if form else None
    status, span = status_of(e)
    put("status", status, span)
    for i in (1, 2, 3):
        n = e.get(f"naeringskode{i}")
        if isinstance(n, dict) and n.get("kode"):
            put("nace" if i == 1 else f"nace_{i}", {"code": n["kode"], "description": n.get("beskrivelse")},
                _span(f"naeringskode{i}.kode", n["kode"]))
    for key, field in (("forretningsadresse", "registered_address"), ("postadresse", "postal_address")):
        addr = _address(e.get(key))
        put(field, addr, _span(key, e.get(key)))
    emp = e.get("antallAnsatte")
    if isinstance(emp, int) and not isinstance(emp, bool):
        put("employees", emp, _span("antallAnsatte", emp))  # 0 is a real value and is preserved
    elif e.get("harRegistrertAntallAnsatte") is False:
        cs.unavailable("employees", "not_available", note="harRegistrertAntallAnsatte=false", source_url=url,
                       source_class=LIVE, retrieved_at=f.retrieved_at, sha256=f.sha256)
    for key, field in (("stiftelsesdato", "founded"), ("registreringsdatoEnhetsregisteret", "registered_at"),
                       ("sisteInnsendteAarsregnskap", "latest_accounts_year"), ("maalform", "language_form")):
        put(field, e.get(key), _span(key, e.get(key)))
    if isinstance(e.get("registrertIMvaregisteret"), bool):
        put("vat_registered", e["registrertIMvaregisteret"], _span("registrertIMvaregisteret", e["registrertIMvaregisteret"]))
    sector = e.get("institusjonellSektorkode")
    if isinstance(sector, dict) and sector.get("kode"):
        put("institutional_sector", {"code": sector["kode"], "description": sector.get("beskrivelse")},
            _span("institusjonellSektorkode.kode", sector["kode"]))
    purpose = e.get("vedtektsfestetFormaal")
    purpose = " ".join(purpose) if isinstance(purpose, list) else purpose
    put("registered_purpose", purpose, _span("vedtektsfestetFormaal", e.get("vedtektsfestetFormaal")))
    activity = e.get("aktivitet")
    activity = " ".join(activity) if isinstance(activity, list) else activity
    put("registered_activity", activity, _span("aktivitet", e.get("aktivitet")))
    put("registry_website", e.get("hjemmeside"), _span("hjemmeside", e.get("hjemmeside")))
    for key, field in (("telefon", "phone"), ("mobil", "mobile"), ("epostadresse", "email")):
        put(field, e.get(key), _span(key, e.get(key)))
    if isinstance(e.get("erIKonsern"), bool):
        put("in_group", e["erIKonsern"], _span("erIKonsern", e["erIKonsern"]))
    names = [{"name": h["navn"], "from": h.get("fraDato"), "to": h.get("tilDato")}
             for h in e.get("historiskeNavn") or [] if isinstance(h, dict) and h.get("navn")]
    put("previous_names", names, _span("historiskeNavn", [n["name"] for n in names]))
    cap = e.get("kapital")
    if isinstance(cap, dict) and isinstance(cap.get("belop"), (int, float)):
        put("share_capital", {"amount": cap["belop"], "currency": cap.get("valuta"), "type": cap.get("type"),
                              "registered": cap.get("innfortDato")}, _span("kapital.belop", cap["belop"]))
    return True


def universe_claims(cs: ClaimSet, row: dict[str, Any], retrieved_at: str | None = None) -> None:
    """Fallback identity facts from the frozen universe row (0 requests). Evidence is the universe snapshot."""
    at = retrieved_at or utc_now()

    def put(field: str, value: Any, key: str) -> None:
        if value in (None, "", [], {}):
            return
        cs.available(field, value, confidence=CONF, source_url=UNIVERSE_URL, source_class=BULK,
                     retrieved_at=at, sha256=UNIVERSE_SHA, span=_span(key, row.get(key)),
                     method="universe_row_field")

    put("legal_name", row.get("name"), "name")
    if row.get("legal_form"):
        put("legal_form", {"code": row["legal_form"]}, "legal_form")
    adverse = row.get("bankrupt") or row.get("liquidating")
    if "bankrupt" in row and "liquidating" in row:
        put("status", "bankrupt" if row.get("bankrupt") else "liquidating" if row.get("liquidating") else "active",
            "bankrupt" if adverse else "liquidating")
    if row.get("industry_code") and row["industry_code"] != "00.000":
        put("nace", {"code": row["industry_code"], "description": row.get("industry_label")}, "industry_code")
    if row.get("municipality"):
        put("municipality", {"name": row["municipality"], "number": row.get("municipality_number")}, "municipality")
    if isinstance(row.get("employees"), int):
        put("employees", row["employees"], "employees")
    put("registry_website", row.get("website"), "website")
    put("latest_accounts_year", row.get("latest_submitted_accounts"), "latest_submitted_accounts")


def roles_claims(cs: ClaimSet, org: str, f: Fetched) -> None:
    url = ROLES_URL.format(org=org)
    if f.status in (404, 410):
        cs.unavailable("roles", "not_available", note=f"HTTP {f.status}: no role record", source_url=url,
                       source_class=ROLES, retrieved_at=f.retrieved_at, sha256=f.sha256)
        return
    if not f.ok or not isinstance(f.body, dict):
        cs.unavailable("roles", "failed", note=f"roles fetch failed: {f.error}")
        return
    roles: list[dict[str, Any]] = []
    for group in f.body.get("rollegrupper") or []:
        for item in group.get("roller") or []:
            if item.get("avregistrert") or item.get("fratraadt"):
                continue
            person, entity = item.get("person") or {}, item.get("enhet") or {}
            n = person.get("navn") or {}
            name = " ".join(x for x in (n.get("fornavn"), n.get("mellomnavn"), n.get("etternavn")) if x) \
                or (entity.get("navn") if isinstance(entity.get("navn"), str) else None)
            role = _g(item, "type", "beskrivelse")
            if not (name and role):
                continue
            roles.append({k: v for k, v in {
                "name": name, "role": role, "role_code": _g(item, "type", "kode"),
                "holder_organisation_number": entity.get("organisasjonsnummer"),
                "last_changed": group.get("sistEndret")}.items() if v})
    if not roles:
        cs.unavailable("roles", "not_available", note="roles endpoint returned no active role holders",
                       source_url=url, source_class=ROLES, retrieved_at=f.retrieved_at, sha256=f.sha256)
        return
    roles.sort(key=lambda r: (r["role"], r["name"]))
    cs.available("roles", roles, confidence=CONF, source_url=url, source_class=ROLES,
                 retrieved_at=f.retrieved_at, sha256=f.sha256,
                 span="; ".join(f"{r['role']}: {r['name']}" for r in roles)[:2000],
                 method="brreg_roles_bulk_snapshot" if f.via == "bulk" else "brreg_roles_json")


def subunit_claims(cs: ClaimSet, org: str, f: Fetched) -> None:
    url = SUBUNITS_URL.format(org=org)
    if f.status in (404, 410) or (f.ok and not (_g(f.body, "_embedded", "underenheter") or [])):
        cs.unavailable("workplaces", "not_available", note="checked: no registered subunits", source_url=url,
                       source_class=SUBUNITS, retrieved_at=f.retrieved_at, sha256=f.sha256)
        return
    if not f.ok:
        cs.unavailable("workplaces", "failed", note=f"subunits fetch failed: {f.error}")
        return
    units = []
    for u in _g(f.body, "_embedded", "underenheter") or []:
        addr = _address(u.get("beliggenhetsadresse") or u.get("postadresse"))
        units.append({k: v for k, v in {
            "organisation_number": u.get("organisasjonsnummer"), "name": u.get("navn"), "address": addr,
            "nace": _g(u, "naeringskode1", "kode"), "employees": u.get("antallAnsatte")}.items()
            if v not in (None, "", {})})
    units.sort(key=lambda x: x.get("organisation_number", ""))
    cs.available("workplaces", units, confidence=CONF, source_url=url, source_class=SUBUNITS,
                 retrieved_at=f.retrieved_at, sha256=f.sha256,
                 span="; ".join(f"{u.get('organisation_number')} {u.get('name')}" for u in units)[:2000],
                 method="brreg_subunits_bulk_snapshot" if f.via == "bulk" else "brreg_subunits_json")
