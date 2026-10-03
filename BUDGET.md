# Budget and run control

Limits are internal safety limits (the official limits are not published): 45 min wall clock, 2,000 outbound
requests, $10 declared external cost; target < 15 requests per company and $0 on free models.
Override with `.env`: `REQUEST_BUDGET_TOTAL`, `REQUEST_BUDGET_PER_COMPANY`, `WALL_CLOCK_SECONDS`,
`CUTOFF_MARGIN_SECONDS`, `MAX_WORKERS`, `BULK_THRESHOLD`.

## Where requests go
| module | per-company cost | alternative |
|---|---|---|
| accounts (Regnskapsregisteret) | 1 | none (no bulk exists) |
| entity record | 1 | **free** from `--bulk` CSV (155 MB, supplied by the evaluator) |
| roles | 1 | **1 request total**: `roller/totalbestand` (130 MB gz), filtered while streaming |
| workplaces (subunits) | 1 | **1 request total**: `underenheter/lastned` (89 MB gz) |
| website | robots + home + up to 2 about/contact pages + careers + feed/news (+1 LLM): planner estimate 7 | none; 0 requests when no site is listed (~89% of companies) |

Bulk roles/subunits are used automatically from `BULK_THRESHOLD` (300) companies upward (`--bulk-register on|off`
to force). They were verified on live data: 132 comparisons against per-company responses, 0 differences.
If a bulk download fails, those modules fall back to per-company requests.

## Planner (`planner.py`)
Tiers are filled across the batch in value-per-request order: accounts, web, roles, workplaces, entity detail.
8% is reserved for retries. The plan is recomputed every chunk from the REAL remaining budget, so over/under
spend self-corrects. Bank/insurer NACE (64-66) gets one accounts attempt (the endpoint often answers HTTP 500).

## Hard stops
`Budget` holds the global total, the per-company cap and a deadline (`start + 45 min - margin`). After the deadline
or on SIGINT/SIGTERM every request is refused instantly; remaining companies get zero-network placeholder envelopes
(register facts from the universe row, `terminal_status=partial`, explicit error). `envelopes.jsonl` is rewritten
atomically at every checkpoint and ALWAYS contains one line per input (unprocessed ones as placeholders), so a hard
kill still leaves a complete, valid file.

## Benchmark
`make bench` (or `uv run python scripts/benchmark.py [--rerun]`) runs `samples/daily.jsonl` (100 companies) and
checks time, requests, cost, requests/company, one-envelope-per-input and contract validation against the limits.
