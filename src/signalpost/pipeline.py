"""Register-only pipeline for one company -> one terminal Envelope. Never raises: failures become states."""
from __future__ import annotations

import time
from typing import Any

from . import accounts, register
from .claims import ClaimSet
from .explain import explain
from .httpcache import ApiClient, Fetched, utc_now
from .models import Envelope, Operations, Run
from .refresh import apply_refresh
from .store import SnapshotStore
from .web.enrich import enrich_website
from .web.fetch import WebFetcher
from .web.identity import CompanyIdentity
from .web.llm import LlmClient

# Priority order under budget pressure: most valuable per request first.
DEFAULT_MODULES = ("financials", "entity", "roles", "subunits")  # "history" is opt-in (rate-limited)


def _identity(org: str, cs: ClaimSet, row: dict[str, Any] | None) -> CompanyIdentity | None:
    """Identity anchor for the web gate, built only from official register claims (never from the web)."""
    c = {x.field: x.value for x in cs.claims if x.availability == "available"}
    name = c.get("legal_name") or (row or {}).get("name")
    if not name:
        return None
    addr = c.get("registered_address") or {}
    muni = (c.get("municipality") or {}).get("name") or addr.get("municipality") or (row or {}).get("municipality")
    return CompanyIdentity(org=org, name=name, street=addr.get("street"), postcode=addr.get("postcode"),
                           city=addr.get("city"), municipality=muni, phone=c.get("phone") or c.get("mobile"))


def register_envelope(org: str, client: ApiClient, *, run_id: str, universe_row: dict[str, Any] | None = None,
                      modules: tuple[str, ...] = DEFAULT_MODULES, fetcher: WebFetcher | None = None,
                      llm: LlmClient | None = None, store: SnapshotStore | None = None,
                      previous: Envelope | None = None, now: str | None = None) -> Envelope:
    """`previous` (e.g. from --previous) overrides the store's latest snapshot. With a store, the new state is saved."""
    started, t0 = utc_now(), time.monotonic()
    if previous is None and store is not None:
        previous = store.latest(org)
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
        if fetcher is not None:
            website = next((x.value for x in cs.claims if x.field == "registry_website" and x.availability == "available"), None)
            ident = _identity(org, cs, universe_row)
            if ident is not None:
                llm_before = llm.thread_requests() if llm else 0
                prior_sha = store.get_web_state(org)[0] if store else None
                web = enrich_website(cs, ident, website, fetcher, llm, prior_sha=prior_sha, previous=previous)
                if store and web.homepage_sha:
                    store.set_web_state(org, web.homepage_sha, website)
                requests += web.requests + ((llm.thread_requests() - llm_before) if llm else 0)
                # informational: facts the verifier refused to publish (not a run error)
                errors.extend({"module": "web", "kind": "dropped_fact", **d} for d in web.dropped)
    except Exception as exc:  # noqa: BLE001 - one bad company must never drop its envelope
        errors.append({"module": "pipeline", "error": f"{type(exc).__name__}: {str(exc)[:200]}"})
        status = "failed"
    env = Envelope(
        organisation_number=org,
        run=Run(run_id=run_id, started_at=started, completed_at=utc_now(), terminal_status=status),
        claims=cs.sorted_claims(), evidence=cs.evidence, errors=errors,
        operations=Operations(requests=requests, runtime_ms=int((time.monotonic() - t0) * 1000)),
    )
    if previous is not None or store is not None:
        env = apply_refresh(previous, env, now or env.run.completed_at)
    env = env.model_copy(update={"explanation": explain(env, had_previous=previous is not None)})
    if store is not None and env.run.terminal_status != "failed":
        store.save(env)
    return env
