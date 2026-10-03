"""Self-contained, responsive HTML report of a run (no external assets, readable without JavaScript).

Every value comes from registers or third-party web pages, so everything is HTML-escaped and only http(s) URLs
become links. A tiny inline script adds search/filter chips (progressive enhancement).
"""
from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

MAX_COMPANIES = 500
SECTIONS = [
    ("Legal identity", ("legal_name", "legal_form", "status", "registered_address", "postal_address", "nace",
                        "founded", "registered_at", "employees", "vat_registered", "institutional_sector",
                        "registered_purpose", "registered_activity", "in_group", "previous_names", "share_capital",
                        "phone", "mobile", "email", "registry_website", "latest_accounts_year", "registry_record",
                        "municipality", "language_form")),
    ("Financials", ("financials", "financial_history_years")),
    ("Leadership", ("roles",)),
    ("Registered workplaces", ("workplaces",)),
    ("Website and public profiles", ("official_website", "website_", "contact_", "social_", "products_")),
    ("Hiring and public activity", ("careers_page", "open_positions", "hiring_status", "public_activity",
                                    "latest_activity_date")),
]
E = html.escape


def safe_url(u: str | None) -> str | None:
    p = urlparse(u or "")
    return u if p.scheme in ("http", "https") and p.netloc else None


def fmt(v: Any) -> str:
    if isinstance(v, dict):
        if set(v) >= {"amount"}:
            a = v["amount"]
            n = f"{a:,.0f}" if float(a).is_integer() else f"{a:,.2f}"
            return E(f"{n.replace(',', ' ')} {v.get('currency') or ''}".strip())
        return E(", ".join(f"{k}: {x}" for k, x in v.items() if x not in (None, "")))
    if isinstance(v, list):
        items = [fmt(x) for x in v[:10]]
        more = f"<li>+{len(v) - 10} more</li>" if len(v) > 10 else ""
        return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + more + "</ul>"
    return E(str(v))


def _section_of(field: str) -> str:
    for title, keys in SECTIONS:
        if any(field == k or (k.endswith("_") and field.startswith(k)) or (k == "financials" and field.startswith(
                ("financials.", "financials_"))) or (k == "nace" and field.startswith("nace")) for k in keys):
            return title
    return "Other"


def _fact(c: dict[str, Any], ev: dict[str, dict[str, Any]]) -> str:
    e = ev.get((c.get("evidence_ids") or [None])[0]) or {}
    url = safe_url(e.get("source_url"))
    src = (f'<a href="{E(url, quote=True)}" rel="noopener noreferrer nofollow">{E(urlparse(url).netloc)}</a>'
           if url else E(e.get("source_url", "") or ""))
    day = E((e.get("retrieved_at") or "")[:10])
    period = f' <span class="muted">period {E(c["reporting_period"])}</span>' if c.get("reporting_period") else ""
    carried = ' <span class="tag warn">kept from earlier run</span>' if c.get("carried_forward") else ""
    snippet = (f'<details class="snip"><summary>evidence</summary><blockquote>{E(e["claim_span"])}</blockquote>'
               f'<span class="muted">sha256 {E((e.get("content_sha256") or "n/a")[:16])} · {E(e.get("source_class", ""))}'
               f' · {E(e.get("extraction_method") or "")}</span></details>') if e.get("claim_span") else ""
    if c.get("availability") == "available":
        value = fmt(c.get("value"))
        tag = ""
    else:
        value = f'<span class="muted">{E(c.get("note") or "")}</span>'
        tag = f' <span class="tag {"bad" if c["availability"] in ("failed", "blocked") else "neutral"}">' \
              f'{E(c["availability"].replace("_", " "))}</span>'
    return (f'<div class="fact"><div class="k">{E(c["field"].replace("_", " "))}{tag}</div>'
            f'<div class="v">{value}{period}{carried}</div>'
            f'<div class="s">{src} · {day} · conf {c.get("confidence", "")}{snippet}</div></div>')


def _company(env: dict[str, Any]) -> str:
    ev = {x["id"]: x for x in env.get("evidence", [])}
    claims = env.get("claims", [])
    name = next((c["value"] for c in claims if c["field"] == "legal_name" and c.get("availability") == "available"),
                "(name not available)")
    status = next((c["value"] for c in claims if c["field"] == "status" and c.get("availability") == "available"), None)
    site = next((c for c in claims if c["field"] == "official_website"), None)
    has_site = bool(site and site.get("availability") == "available")
    changes = env.get("changes", [])
    run_status = env["run"]["terminal_status"]
    buckets: dict[str, list[str]] = {}
    for c in sorted(claims, key=lambda c: c["field"]):
        buckets.setdefault(_section_of(c["field"]), []).append(_fact(c, ev))
    body = []
    for title in [t for t, _ in SECTIONS] + ["Other"]:
        if buckets.get(title):
            body.append(f"<section><h4>{E(title)}</h4>{''.join(buckets[title])}</section>")
    if changes:
        rows = "".join(
            f'<li><b>{E(ch["change_type"].replace("_", " "))}</b>{" (material)" if ch.get("material") else ""}: '
            f'{E(ch["field"])} — {E(str(ch.get("old_value"))[:120])} → {E(str(ch.get("new_value"))[:120])} '
            f'<span class="muted">detected {E(ch.get("detected_at", "")[:10])}</span></li>' for ch in changes)
        body.append(f"<section><h4>Changes since previous run</h4><ul>{rows}</ul></section>")
    if env.get("errors"):
        errs = "".join(f"<li>{E(str({k: v for k, v in x.items() if k != 'dropped_fact'})[:200])}</li>"
                       for x in env["errors"][:10])
        body.append(f"<section><h4>Run notes</h4><ul>{errs}</ul></section>")
    badge = (f'<span class="tag {"bad" if status and status != "active" else "ok"}">{E(str(status))}</span>'
             if status else "")
    flags = " ".join(k for k, on in (("site", has_site), ("changes", bool(changes)),
                                     ("issues", run_status != "completed")) if on)
    search = E(f"{name} {env['organisation_number']}".casefold(), quote=True)
    n_av = sum(1 for c in claims if c.get("availability") == "available")
    return (f'<details class="co" data-search="{search}" data-flags="{flags}"><summary><span class="nm">{E(str(name))}'
            f'</span> <span class="muted">{E(env["organisation_number"])}</span> {badge}'
            f' <span class="muted">{n_av} facts{" · website verified" if has_site else ""}'
            f'{" · " + str(len(changes)) + " change(s)" if changes else ""}'
            f'{" · " + run_status if run_status != "completed" else ""}</span></summary>'
            f'<p class="why">{E(env.get("explanation") or "")}</p>{"".join(body)}</details>')


CSS = """
:root{--bg:#fff;--fg:#1c2330;--mut:#5b6678;--line:#dde2ea;--card:#f6f8fb;--ok:#14733f;--bad:#b3261e;--warn:#8a5a00;--acc:#1f5fbf}
@media (prefers-color-scheme:dark){:root{--bg:#10151d;--fg:#e6eaf0;--mut:#9aa6b8;--line:#2a3342;--card:#171e29;--ok:#4cc38a;--bad:#ff7b72;--warn:#e3b341;--acc:#79b0ff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:980px;margin:0 auto;padding:16px}h1{font-size:1.5rem;margin:.2em 0}h4{margin:.9em 0 .3em;font-size:.95rem;text-transform:uppercase;letter-spacing:.04em;color:var(--mut)}
.muted{color:var(--mut);font-size:.9em}a{color:var(--acc)}.sum{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;margin:12px 0}
.sum div{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 10px}.sum b{display:block;font-size:1.25rem}
.bar{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}input[type=search]{flex:1 1 220px;padding:10px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--fg);font:inherit}
button.chip{padding:8px 12px;border:1px solid var(--line);border-radius:999px;background:var(--card);color:var(--fg);font:inherit;cursor:pointer}button.chip[aria-pressed=true]{border-color:var(--acc);color:var(--acc)}
details.co{border:1px solid var(--line);border-radius:10px;margin:8px 0;background:var(--card)}details.co>summary{padding:10px 12px;cursor:pointer;list-style:none}.nm{font-weight:600}
details.co>section,details.co>p{margin:0;padding:0 12px 8px}.why{padding-top:2px!important}.fact{display:grid;grid-template-columns:1fr;gap:2px;padding:6px 0;border-top:1px solid var(--line)}
.fact .k{font-weight:600;text-transform:capitalize}.fact .v{overflow-wrap:anywhere}.fact .v ul{margin:.2em 0;padding-left:1.2em}.fact .s{font-size:.85em;color:var(--mut)}
@media (min-width:720px){.fact{grid-template-columns:200px 1fr 260px;gap:12px}}
.tag{font-size:.75em;padding:1px 7px;border-radius:999px;border:1px solid var(--line)}.tag.ok{color:var(--ok)}.tag.bad{color:var(--bad)}.tag.warn{color:var(--warn)}.tag.neutral{color:var(--mut)}
blockquote{margin:4px 0;padding:4px 10px;border-left:3px solid var(--line);color:var(--fg);overflow-wrap:anywhere}.snip summary{cursor:pointer;display:inline}
.hidden{display:none}table{border-collapse:collapse;width:100%}td,th{padding:4px 8px;border-bottom:1px solid var(--line);text-align:left;font-size:.9em}
"""
JS = """
(function(){var q=document.getElementById('q'),cards=[].slice.call(document.querySelectorAll('details.co')),
chips=[].slice.call(document.querySelectorAll('button.chip')),flag='';
function run(){var t=(q.value||'').toLowerCase();cards.forEach(function(c){
var ok=c.dataset.search.indexOf(t)>-1&&(!flag||(' '+c.dataset.flags+' ').indexOf(' '+flag+' ')>-1);c.classList.toggle('hidden',!ok);});}
q.addEventListener('input',run);chips.forEach(function(b){b.addEventListener('click',function(){
flag=b.getAttribute('aria-pressed')==='true'?'':b.dataset.flag;chips.forEach(function(x){x.setAttribute('aria-pressed',x===b&&flag?'true':'false');});run();});});})();
"""


def render(envs: list[dict[str, Any]], report: dict[str, Any], max_companies: int = MAX_COMPANIES) -> str:
    ops = report.get("operations", {})
    cov = report.get("coverage_pct", {})

    def priority(e: dict[str, Any]) -> tuple:
        has_site = any(c["field"] == "official_website" and c.get("availability") == "available" for c in e["claims"])
        return (e["run"]["terminal_status"] == "completed", not e.get("changes"), not has_site)
    shown = sorted(envs, key=priority)[:max_companies] if len(envs) > max_companies else envs
    note = (f'<p class="muted">Showing {len(shown)} of {len(envs)} companies (profiles with issues, changes or a '
            f'verified website first). The complete data is in envelopes.jsonl.</p>') if len(shown) < len(envs) else ""
    stat = lambda label, val: f"<div><b>{E(str(val))}</b>{E(label)}</div>"
    cov_rows = "".join(f"<tr><td>{E(k.replace('_', ' '))}</td><td>{v}%</td></tr>" for k, v in cov.items())
    page = [
        '<!doctype html><html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        f"<title>Signalpost run {E(str(report.get('run_id', '')))}</title><style>{CSS}</style></head><body><main>",
        (f"<h1>Signalpost company profiles</h1><p class=\"muted\">Run {E(str(report.get('run_id', '')))} · "
         f"{E(str(report.get('completed_at', ''))[:19])} · every fact links to its source, retrieval date and evidence "
         "snippet; missing information is shown as such, never as zero.</p>"),
        '<div class="sum">' + stat("companies", report.get("envelopes_written", len(envs)))
        + stat("requests", ops.get("requests_total_budgeted", "-")) + stat("seconds", ops.get("wall_clock_seconds", "-"))
        + stat("cost USD", ops.get("third_party_cost_usd", "-")) + stat("changes", report.get("changes_total", 0)) + "</div>",
        f"<details><summary>Coverage by field</summary><table>{cov_rows}</table></details>", note,
        ('<div class="bar"><input id="q" type="search" placeholder="Search name or organisation number" '
         'aria-label="Search">'
         '<button class="chip" data-flag="site" aria-pressed="false">Verified website</button>'
         '<button class="chip" data-flag="changes" aria-pressed="false">Changes</button>'
         '<button class="chip" data-flag="issues" aria-pressed="false">Issues</button></div>'),
        "".join(_company(e) for e in shown) or "<p>No companies.</p>",
        f"</main><script>{JS}</script></body></html>"]
    return "\n".join(page)


def write_report(envs_models: list[Any], report: dict[str, Any], path: str | Path) -> None:
    envs = [e.model_dump(mode="json") if hasattr(e, "model_dump") else e for e in envs_models]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(render(envs, report), encoding="utf-8")


def strip_scripts(s: str) -> str:  # test helper: remove the one trusted inline script
    return re.sub(r"<script>.*?</script>", "", s, flags=re.DOTALL)
