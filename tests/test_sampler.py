import json
from pathlib import Path

import pytest

from signalpost.sample import build_samples
from signalpost.universe import load_universe, valid_orgnr

REAL = Path(__file__).resolve().parents[1] / "data" / "orgs.json"


def make_org(base8: str) -> str:
    w = (3, 2, 7, 6, 5, 4, 3, 2)
    r = 11 - sum(int(a) * b for a, b in zip(base8, w, strict=True)) % 11
    r = 0 if r == 11 else r
    return base8 + str(r) if r != 10 else ""


def test_mod11_known_valid_and_invalid():
    assert valid_orgnr("990918546") and valid_orgnr("993578843")
    assert not valid_orgnr("990918547")
    assert not valid_orgnr("12345") and not valid_orgnr("99091854a") and not valid_orgnr("")


def synth(n=400):
    rows, i = [], 81000000
    while len(rows) < n:
        i += 1
        org = make_org(str(i))
        if org:
            form = "ENK" if len(rows) % 7 == 0 else "AS"
            rows.append({"organisation_number": org, "name": f"N{i}", "legal_form": form,
                         "employees": (len(rows) % 120) or None, "website": "x.no" if len(rows) % 5 == 0 else "",
                         "industry_code": "64.200" if len(rows) % 9 == 0 else "47.110"})
    return rows


def test_load_drops_invalid_and_duplicates(tmp_path):
    good = synth(5)
    lines = [json.dumps(r) for r in good] + [json.dumps(good[0]), json.dumps({**good[1], "organisation_number": "990918547"})]
    p = tmp_path / "u.jsonl"
    p.write_text("\n".join(lines))
    rows, rep = load_universe(p)
    assert (rep.total_rows, rep.invalid_mod11, rep.duplicates, rep.kept) == (7, 1, 1, 5)
    assert [r["organisation_number"] for r in rows] == sorted(r["organisation_number"] for r in good)


def test_lfs_pointer_detected(tmp_path):
    p = tmp_path / "u.json"
    p.write_text("version https://git-lfs.github.com/spec/v1\noid sha256:x\nsize 1\n")
    with pytest.raises(RuntimeError, match="LFS"):
        load_universe(p)


def test_samples_reproducible_and_disjoint():
    rows = sorted(synth(400), key=lambda r: r["organisation_number"])
    a = build_samples(rows, seed=1, submission=150, daily=20, per_stratum=2)
    b = build_samples(rows, seed=1, submission=150, daily=20, per_stratum=2)
    c = build_samples(rows, seed=2, submission=150, daily=20, per_stratum=2)
    assert a == b and a != c
    ids = [x["organisation_number"] for k in a.values() for x in k]
    assert len(ids) == len(set(ids)) and len(a["daily"]) == 20 and len(a["submission"]) == 150


@pytest.mark.skipif(not REAL.exists() or REAL.stat().st_size < 10_000, reason="orgs.json not available")
def test_real_universe_counts():
    rows, rep = load_universe(REAL)
    assert rep.kept == 411160 and rep.invalid_mod11 == 0 and rep.duplicates == 0
    s = build_samples(rows)
    assert len(s["submission"]) == 1500 and len(s["daily"]) == 100
