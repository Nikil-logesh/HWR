"""The Brreg bulk CSV (real rows, recorded 2026-10-03) must yield the same entity claims as the live JSON endpoint."""
import csv
import glob
import json
from pathlib import Path

import pytest

from signalpost.claims import ClaimSet
from signalpost.httpcache import Fetched
from signalpost.inputs import csv_row_to_entity, load_registry_rows
from signalpost.register import entity_claims

FIX = Path(__file__).parent / "fixtures" / "recorded"
ROWS = {r["organisasjonsnummer"]: r for r in csv.DictReader((FIX / "bulk_rows.csv").open(encoding="utf-8", newline=""))}
RECORDED = sorted(glob.glob(str(FIX / "[0-9]*.json")))
ONLY_LIVE = {"previous_names"}  # historiskeNavn is not a column of the bulk CSV


def claims(entity, via):
    cs = ClaimSet()
    assert entity_claims(cs, entity["organisasjonsnummer"], Fetched("u", 200, entity, "h", "t", via=via))
    return {c.field: c for c in cs.claims}


@pytest.mark.parametrize("path", RECORDED, ids=lambda p: Path(p).stem)
def test_csv_row_gives_same_claims_as_live_json(path):
    rec = json.loads(Path(path).read_text(encoding="utf-8"))
    live = claims(rec["responses"]["entity"]["body"], "api")
    bulk = claims(csv_row_to_entity(ROWS[rec["org"]]), "bulk")
    assert {k: v.value for k, v in bulk.items()} == {k: v.value for k, v in live.items() if k not in ONLY_LIVE}
    assert all(c.evidence_ids for c in bulk.values())


def test_bulk_provenance_names_the_method_and_keeps_the_resolvable_url():
    org = "923609016"
    cs = claims(csv_row_to_entity(ROWS[org]), "bulk")
    c = ClaimSet()
    entity_claims(c, org, Fetched(f"https://x/{org}", 200, csv_row_to_entity(ROWS[org]), "h", "t", via="bulk"))
    assert {e.extraction_method for e in c.evidence} == {"brreg_bulk_csv_field"} and cs["legal_name"].value == "EQUINOR ASA"


def test_typing_of_csv_cells():
    e = csv_row_to_entity(ROWS["923609016"])
    assert e["antallAnsatte"] == 21272 and e["konkurs"] is False and e["erIKonsern"] is True
    assert e["forretningsadresse"]["adresse"] == ["Forusbeen 50"] and e["kapital"]["belop"] == 5976872600.0
    assert e["registrertIMvaregisteret"] is True and "historiskeNavn" not in e


def test_load_registry_rows_attaches_full_entity_for_csv(tmp_path):
    rows = load_registry_rows(FIX / "bulk_rows.csv", {"923609016", "000000000"})
    assert set(rows) == {"923609016"} and rows["923609016"]["name"] == "EQUINOR ASA"
    assert rows["923609016"]["_entity"]["forretningsadresse"]["poststed"] == "STAVANGER"
