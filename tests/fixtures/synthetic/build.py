"""Generates SYNTHETIC Brreg-shaped fixtures (organisation numbers and values are invented, NOT recorded).

Shapes follow the field names used by the Builderr kit normalizers. Replace with live recordings via
scripts/record_fixtures.py once data.brreg.no is reachable. Run: python tests/fixtures/synthetic/build.py
"""
import json
from pathlib import Path

W = (3, 2, 7, 6, 5, 4, 3, 2)


def org(base8: str) -> str:
    """Return base8 + check digit; if the base has no valid check digit (mod-11 = 10), take the next base."""
    while True:
        r = 11 - sum(int(a) * b for a, b in zip(base8, W, strict=True)) % 11
        r = 0 if r == 11 else r
        if r != 10:
            return base8 + str(r)
        base8 = str(int(base8) + 1)


def addr(street, post, city, kommune, knr):
    return {"land": "Norge", "landkode": "NO", "postnummer": post, "poststed": city, "adresse": [street],
            "kommune": kommune, "kommunenummer": knr}


def acct(start, end, rev, op, pbt, res, assets, eq, debt, kind="SELSKAP"):
    return {"id": 1, "regnskapstype": kind, "valuta": "NOK", "regnskapsperiode": {"fraDato": start, "tilDato": end},
            "resultatregnskapResultat": {"driftsresultat": {"driftsinntekter": {"sumDriftsinntekter": rev},
                                                            "driftsresultat": op},
                                         "ordinaertResultatFoerSkattekostnad": pbt, "aarsresultat": res},
            "eiendeler": {"sumEiendeler": assets},
            "egenkapitalGjeld": {"egenkapital": {"sumEgenkapital": eq}, "gjeldOversikt": {"sumGjeld": debt}}}


def entity(o, name, form, desc, nace, ncode, a, **kw):
    e = {"organisasjonsnummer": o, "navn": name, "organisasjonsform": {"kode": form, "beskrivelse": desc},
         "naeringskode1": {"kode": nace, "beskrivelse": ncode}, "forretningsadresse": a, "konkurs": False,
         "underAvvikling": False, "underTvangsavviklingEllerTvangsopplosning": False,
         "registreringsdatoEnhetsregisteret": "2015-03-02", "registrertIMvaregisteret": True}
    e.update(kw)
    return e


def role(kind, desc, first, last):
    return {"type": {"kode": kind, "beskrivelse": desc}, "person": {"navn": {"fornavn": first, "etternavn": last},
            "fodselsdato": "1970-01-01"}, "avregistrert": False}


CASES = {}
# 1 active AS, website, full data, accounts, roles, subunit
o = org("91000001")
CASES["active_as_with_website"] = dict(org=o, entity=entity(
    o, "SYNTETISK TESTSELSKAP AS", "AS", "Aksjeselskap", "62.010", "Programmeringstjenester",
    addr("Testveien 1", "0150", "OSLO", "OSLO", "0301"), antallAnsatte=12, stiftelsesdato="2015-02-20",
    hjemmeside="www.syntetisk-test.example", sisteInnsendteAarsregnskap="2025",
    vedtektsfestetFormaal=["Utvikling av programvare."]),
    accounts=[acct("2025-01-01", "2025-12-31", 12500000, 900000, 850000, 700000, 5000000, 2100000, 2900000)],
    roles={"rollegrupper": [{"type": {"kode": "STYR", "beskrivelse": "Styre"}, "sistEndret": "2024-05-01",
                             "roller": [role("LEDE", "Styrets leder", "Kari", "Nordmann"),
                                        role("MEDL", "Styremedlem", "Ola", "Hansen")]},
                            {"type": {"kode": "DAGL", "beskrivelse": "Daglig leder"}, "roller": [
                                role("DAGL", "Daglig leder", "Kari", "Nordmann")]}]},
    subunits={"_embedded": {"underenheter": [{"organisasjonsnummer": org("91100001"), "navn": "SYNTETISK TEST AVD BERGEN",
              "beliggenhetsadresse": addr("Havnegata 2", "5003", "BERGEN", "BERGEN", "4601"),
              "naeringskode1": {"kode": "62.010"}, "antallAnsatte": 4}]}}, years=["2024", "2025"])
# 2 sole proprietorship, no accounts (404), no roles
o = org("91000002")
CASES["enk_no_accounts"] = dict(org=o, entity=entity(o, "SYNTETISK ENKEL ENK", "ENK", "Enkeltpersonforetak", "96.020",
    "Frisorvirksomhet", addr("Smauet 3", "7010", "TRONDHEIM", "TRONDHEIM", "5001"), antallAnsatte=0),
    accounts=404, roles=404, subunits={}, years=404)
# 3 bankrupt AS
o = org("91000003")
CASES["bankrupt_as"] = dict(org=o, entity=entity(o, "SYNTETISK KONKURS AS", "AS", "Aksjeselskap", "41.200",
    "Oppføring av bygninger", addr("Byggveien 9", "3010", "DRAMMEN", "DRAMMEN", "3005"), konkurs=True,
    konkursdato="2026-06-01", antallAnsatte=3, sisteInnsendteAarsregnskap="2025"),
    accounts=[acct("2025-01-01", "2025-12-31", 0, -120000, -150000, -150000, 80000, -40000, 120000)],
    roles={"rollegrupper": []}, subunits={}, years=["2025"])
# 4 liquidating AS
o = org("91000004")
CASES["liquidating_as"] = dict(org=o, entity=entity(o, "SYNTETISK AVVIKLING AS", "AS", "Aksjeselskap", "70.220",
    "Bedriftsrådgivning", addr("Rådgiverveien 4", "4006", "STAVANGER", "STAVANGER", "1103"), underAvvikling=True),
    accounts=[acct("2025-01-01", "2025-12-31", 450000, 20000, 18000, 14000, 300000, 250000, 50000)],
    roles={"rollegrupper": []}, subunits={}, years=["2025"])
# 5 foreign branch NUF
o = org("91000005")
CASES["nuf_branch"] = dict(org=o, entity=entity(o, "SYNTETISK UTENLANDSK FILIAL", "NUF",
    "Norskregistrert utenlandsk foretak", "46.900", "Uspesialisert engroshandel",
    addr("Kaia 5", "0250", "OSLO", "OSLO", "0301"), antallAnsatte=7),
    accounts=404, roles={"rollegrupper": []}, subunits={}, years=404)
# 6 large ASA with consolidated accounts
o = org("91000006")
CASES["large_asa_consolidated"] = dict(org=o, entity=entity(o, "SYNTETISK STORKONSERN ASA", "ASA", "Allmennaksjeselskap",
    "64.200", "Aktiviteter i holdingselskaper", addr("Konsernplassen 1", "0250", "OSLO", "OSLO", "0301"),
    antallAnsatte=5400, hjemmeside="https://storkonsern.example", sisteInnsendteAarsregnskap="2025"),
    accounts=[acct("2025-01-01", "2025-12-31", 9800000000, 1100000000, 1000000000, 800000000, 12000000000,
                   6000000000, 6000000000, "KONSERN"),
              acct("2025-01-01", "2025-12-31", 12000000, 3000000, 2900000, 2900000, 900000000, 500000000, 400000000)],
    roles={"rollegrupper": [{"type": {"kode": "STYR", "beskrivelse": "Styre"}, "roller": [
        role("LEDE", "Styrets leder", "Eva", "Berg")]}]}, subunits={}, years=["2023", "2024", "2025"])
# 7 housing co-op
o = org("91000007")
CASES["brl_housing_coop"] = dict(org=o, entity=entity(o, "SYNTETISK BORETTSLAG", "BRL", "Boligbyggelag",
    "98.000", "Boligbyggelag", addr("Blokkveien 7", "1337", "SANDVIKA", "BÆRUM", "3024")),
    accounts=[acct("2025-01-01", "2025-12-31", 3200000, 150000, 90000, 90000, 40000000, 5000000, 35000000)],
    roles={"rollegrupper": []}, subunits={}, years=["2025"])
# 8 zero revenue preserved + missing field omitted
o = org("91000018")
rec = acct("2025-01-01", "2025-12-31", 0, -5000, -5000, -5000, 100000, 90000, 10000)
del rec["resultatregnskapResultat"]["ordinaertResultatFoerSkattekostnad"]
CASES["zero_revenue_missing_field"] = dict(org=o, entity=entity(o, "SYNTETISK HVILENDE AS", "AS", "Aksjeselskap",
    "68.200", "Utleie av egen fast eiendom", addr("Eiendomsgata 8", "9008", "TROMSØ", "TROMSØ", "5501"),
    antallAnsatte=0), accounts=[rec], roles={"rollegrupper": []}, subunits={}, years=["2025"])
# 9 foundation, employees not registered
o = org("91000009")
CASES["foundation_no_employee_count"] = dict(org=o, entity=entity(o, "SYNTETISK STIFTELSE", "STI", "Stiftelse",
    "94.991", "Aktiviteter i andre interesseorganisasjoner", addr("Stiftelsesveien 9", "6003", "ÅLESUND", "ÅLESUND", "1507"),
    harRegistrertAntallAnsatte=False), accounts=404, roles={"rollegrupper": []}, subunits={}, years=404)
# 10 deleted entity (HTTP 410)
o = org("91000010")
CASES["deleted_entity_410"] = dict(org=o, entity=410, accounts=404, roles=404, subunits=404, years=404)

if __name__ == "__main__":
    out = Path(__file__).parent
    for name, c in CASES.items():
        (out / f"{name}.json").write_text(json.dumps({"synthetic": True, **c}, ensure_ascii=False, indent=1,
                                                     sort_keys=True) + "\n", encoding="utf-8")
    print(len(CASES), "fixtures written")
