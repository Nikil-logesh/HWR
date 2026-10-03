"""Register-only pipeline for one company -> one terminal Envelope. Never raises: failures become states."""
from __future__ import annotations

import time
from typing import Any

from . import accounts, register
from .claims import ClaimSet
from .httpcache import ApiClient, Fetched, utc_now
from .models import Envelope, Operations, Run

# Priority order under budget pressure: most valuable per request first.
DEFAULT_MODULES = ("financials", "entity", "roles", "subunits", "history")


def register_envelope(org: str, client: ApiClient, *, run_id: str, universe_row: dict[str, Any] | None = None,
                      modules: tuple[str, ...] = DEFAULT_MODULES) -> Envelope:
    started, t0 = utc_now(), time.monotonic()
    cs = ClaimSet()
    errors: list[dict[str, Any]] = []
    requests = 0
    fetched: dict[str, Fetched] = {}
    try:
        urls = {"financials": accounts.ACCOUNTS_URL, "entity": register.ENTITY_URL, "roles": register.ROLES_URL,
                "subunits": register.SUBUNITS_URL, "history": accounts.YEARS_URL}
        for m in modules:
            fetched[m] = client.get_json(urls[m].format(org=org), org)
            requests += fetched[m].requests
            if fetched[m].status in (0, -1):
                errors.append({"module": m, "error": fetched[m].error})
        entity_ok = False
        if "entity" in fetched:
            entity_ok = register.entity_claims(cs, org, fetched["entity"])
        if not entity_ok and universe_row:
            register.universe_claims(cs, universe_row)  # 0-request identity fallback
        if "financials" in fetched:
            accounts.accounts_claims(cs, org, fetched["financials"])
        if "roles" in fetched:
            register.roles_claims(cs, org, fetched["roles"])
        if "subunits" in fetched:
            register.subunit_claims(cs, org, fetched["subunits"])
        if "history" in fetched:
            accounts.years_claims(cs, org, fetched["history"])
        status = "completed" if not errors else "partial"
    except Exception as exc:  # noqa: BLE001 - one bad company must never drop its envelope
        errors.append({"module": "pipeline", "error": f"{type(exc).__name__}: {str(exc)[:200]}"})
        status = "failed"
    return Envelope(
        organisation_number=org,
        run=Run(run_id=run_id, started_at=started, completed_at=utc_now(), terminal_status=status),
        claims=cs.sorted_claims(), evidence=cs.evidence, errors=errors,
        operations=Operations(requests=requests, runtime_ms=int((time.monotonic() - t0) * 1000)),
    )
