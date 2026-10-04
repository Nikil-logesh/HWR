"""Budget planner: decide, per company, which modules to run so the whole batch fits the request budget.

Fill tiers in value-per-request order, each tier across all companies before the next one:
  1. financials  (accounts API: financial family, 1 request)
  2. web         (listed website only: robots + home + ~1.5 pages (+1 LLM) and the entity record for the address
                  signal. Scarce, external, several information types per request)
  3. roles       (leadership, 1 request)
  4. subunits    (registered workplaces, 1 request)
  5. discover    (no registered website: try domain names built from the legal name, ~5 requests, low hit rate)
  6. entity      (extra register detail: address, dates, purpose, phone; identity basics already come free from
                  the universe row)
A reserve (default 8%) covers retries. With a generous budget everything is planned; under pressure the lowest
tiers are dropped first. Re-planning every chunk uses the real remaining budget, so over/under-spend self-corrects.
"""
from __future__ import annotations

from dataclasses import dataclass, field

TIERS = ("financials", "web", "roles", "subunits", "discover", "entity")
MODULE_ORDER = ("financials", "entity", "roles", "subunits")  # fetch order inside a company
DISCOVER_COST = 5  # candidate domains: ~2 requests each (robots + homepage, dead hosts 1), +secondary pages when one matches
WEB_COST = 7  # robots.txt + homepage + about/contact (<=2) + careers + feed/news (worst case 7)
FINANCIAL_SECTOR_DIVISIONS = {"64", "65", "66"}  # banks/insurers: accounts endpoint often returns HTTP 500


@dataclass(frozen=True)
class Company:
    org: str
    has_website: bool = False
    nace: str = ""
    free: frozenset[str] = frozenset()  # modules already available at zero per-company cost (bulk snapshots)
    discoverable: bool = False  # no registered website, but a domain candidate can be built from the legal name

    @property
    def financial_sector(self) -> bool:
        return self.nace[:2] in FINANCIAL_SECTOR_DIVISIONS


@dataclass
class Plan:
    modules: list[str] = field(default_factory=list)
    web: bool = False
    discover: bool = False
    accounts_attempts: int = 3
    est_requests: float = 0.0


def plan_batch(companies: list[Company], budget_left: int, per_company_cap: int = 15, *, llm: bool = False,
               reserve: float = 0.08) -> dict[str, Plan]:
    plans = {c.org: Plan(modules=sorted(c.free), accounts_attempts=1 if c.financial_sector else 3)
             for c in companies}
    avail = budget_left * (1 - reserve)
    web_cost = WEB_COST + (1 if llm else 0)

    def spend(p: Plan, cost: float) -> bool:
        nonlocal avail
        if cost > avail or p.est_requests + cost > per_company_cap:
            return False
        avail -= cost
        p.est_requests += cost
        return True

    for tier in TIERS:
        for c in companies:
            p = plans[c.org]
            if tier == "web":
                if not c.has_website:
                    continue
                need_entity = "entity" not in p.modules  # free (bulk) entity data needs no request
                cost = web_cost + (1 if need_entity else 0)
                if spend(p, cost):
                    p.web = True
                    if need_entity:
                        p.modules.append("entity")
            elif tier == "discover":
                if c.discoverable and not c.has_website and spend(p, DISCOVER_COST):
                    p.discover = True
            elif tier not in p.modules and spend(p, 1):
                p.modules.append(tier)
    for p in plans.values():
        p.modules.sort(key=MODULE_ORDER.index)
    return plans


def summarize(plans: dict[str, Plan]) -> dict[str, float]:
    n = len(plans) or 1
    out: dict[str, float] = {m: 0 for m in TIERS}
    for p in plans.values():
        for m in p.modules:
            out[m] += 1
        out["web"] += 1 if p.web else 0
        out["discover"] += 1 if p.discover else 0
    out["estimated_requests"] = round(sum(p.est_requests for p in plans.values()), 1)
    out["estimated_requests_per_company"] = round(out["estimated_requests"] / n, 2)
    return out
