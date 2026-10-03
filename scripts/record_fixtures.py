#!/usr/bin/env python3
"""Record LIVE Brreg responses for given organisation numbers into tests/fixtures/recorded/<org>.json.

    PYTHONPATH=src python scripts/record_fixtures.py 923609016 ... [--out tests/fixtures/recorded]

Needs network access to data.brreg.no. Recorded files keep status + body per endpoint and the retrieval time,
so tests can replay them with httpx.MockTransport. Respects the history endpoint's ~30 requests/minute limit.
"""
import argparse
import json
import time
from pathlib import Path

import httpx

from signalpost import accounts, register

UA = "signalpost-agent/0.1 (fixture recorder)"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("orgs", nargs="+")
    ap.add_argument("--out", default="tests/fixtures/recorded")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with httpx.Client(headers={"User-Agent": UA, "Accept": "application/json"}, timeout=20) as http:
        for org in args.orgs:
            rec = {"synthetic": False, "org": org, "responses": {}}
            for name, tpl in (("entity", register.ENTITY_URL), ("roles", register.ROLES_URL),
                              ("subunits", register.SUBUNITS_URL), ("accounts", accounts.ACCOUNTS_URL),
                              ("years", accounts.YEARS_URL)):
                url = tpl.format(org=org)
                r = http.get(url)
                rec["responses"][name] = {"url": url, "status": r.status_code,
                                          "body": r.json() if r.status_code == 200 else None,
                                          "retrieved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                time.sleep(2.1 if name == "years" else 0.2)
            (out / f"{org}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
            print("recorded", org)


if __name__ == "__main__":
    main()
