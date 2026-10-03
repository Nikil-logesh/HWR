# Signalpost agent

Evidence-bound company research for Norwegian organisation numbers (Builderr Signalpost challenge).
Official register first; website facts only when the page proves it is the same legal entity.

    make install                                   # uv sync (Python 3.12)
    make test
    make run INPUT=companies.jsonl OUT=out/        # one envelope per input -> out/envelopes.jsonl, out/report.json
    # equivalent: uv run python run_agent.py run --organisations companies.jsonl --out out/

Input: JSON list, JSONL (`{"organisation_number": ...}`) or one number per line. Optional `--bulk` (Brreg bulk CSV or
universe JSONL) gives a free identity fallback; `--previous out_old/envelopes.jsonl` or the default `OUT/state.sqlite`
enables change detection; `--no-web`, `--no-llm`, `--workers N`, `--expected-count N`. Keys go in `.env`
(see `.env.example`); without keys the agent runs deterministic extraction only.

Status: Phases 1-6 done (see ARCHITECTURE.md, DATA_SCHEMA.md, IDENTITY_RESOLUTION.md, REFRESH.md). Full README in Phase 10.
