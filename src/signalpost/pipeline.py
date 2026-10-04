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
from .web.enrich import discover_website, enrich_website
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


def cs_site(cs: ClaimSet) -> str | None:
    return next((str(c.value) for c in cs.claims if c.field == "official_website" and c.availability == "available"), None)


def _discovered_site(previous: Envelope | None) -> str | None:
    """The website an earlier run found by domain candidate (re-checked directly instead of re-guessing)."""
    if previous is None:
        return None
    ev = {e.id: e for e in previous.evidence}
    for c in previous.claims:
        if c.field == "official_website" and c.availability == "available" and any(
                (ev.get(i) and (ev[i].extraction_method or "").startswith("domain_candidate")) for i in c.evidence_ids):
            return str(c.value)
    return None


def register_envelope(org: str, client: ApiClient, *, run_id: str, universe_row: dict[str, Any] | None = None,
                      modules: tuple[str, ...] = DEFAULT_MODULES, fetcher: WebFetcher | None = None,
                      llm: LlmClient | None = None, store: SnapshotStore | None = None,
                      previous: Envelope | None = None, now: str | None = None,
                      accounts_attempts: int | None = None, prefetched: dict[str, Fetched] | None = None,
                      discover: bool = False) -> Envelope:
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
            if prefetched and m in prefetched:  # bulk snapshot: no per-company request
                fetched[m] = prefetched[m]
                continue
            fetched[m] = client.get_json(urls[m].format(org=org), org, accounts_attempts if m == "financials" else None)
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
                if website or not discover:  # no website and no discovery: enrich_website records "not_available", 0 requests
                    web = enrich_website(cs, ident, website, fetcher, llm, prior_sha=prior_sha, previous=previous)
                else:
                    hint = _discovered_site(previous)
                    web = discover_website(cs, ident, fetcher, llm, hint=hint, prior_sha=prior_sha, previous=previous)
                    website = hint or (cs_site(cs) if web.state == "verified" else None)
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


def placeholder_envelope(org: str, universe_row: dict[str, Any] | None, run_id: str, reason: str, *,
                         previous: Envelope | None = None, now: str | None = None) -> Envelope:
    """Terminal envelope built with ZERO network use (cutoff, shutdown, checkpoint): free register facts from the
    universe row, or the last supported profile, plus an explicit error saying what was not done."""
    started = utc_now()
    cs = ClaimSet()
    if universe_row:
        register.universe_claims(cs, universe_row)
    else:
        cs.unavailable("registry_record", "failed", note=reason)
    env = Envelope(organisation_number=org, run=Run(run_id=run_id, started_at=started, completed_at=utc_now(),
                   terminal_status="partial" if universe_row else "failed"), claims=cs.sorted_claims(),
                   evidence=cs.evidence, errors=[{"module": "runner", "error": reason}])
    if previous is not None:
        env = apply_refresh(previous, env, now or env.run.completed_at)
    return env.model_copy(update={"explanation": explain(env, had_previous=previous is not None)})
