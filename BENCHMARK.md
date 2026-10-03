# Model benchmark

**Status: NOT RUN.** The benchmark harness is built and tested, but no model has been measured yet: the build
sandbox had no NVIDIA/Gemini API keys and could not reach company websites. This file therefore contains **no
results and no model recommendation**. `make bench-models` (or the three commands below) overwrites it with
numbers computed from raw per-call rows.

## What it measures
The LLM is used for exactly one job: given an already-fetched, identity-verified page, propose a one-sentence
description and up to six services as **verbatim** text. A code verifier keeps a fact only if its evidence snippet
occurs in the page and contains the value. Identity and financial values are never delegated to a model.

Per model, on the same frozen corpus of 30 identity-verified real company pages plus 3 synthetic prompt-injection
probes (identical prompt, schema and temperature 0): strict-JSON rate, valid-after-recovery rate (fenced / think-tag /
prose-wrapped replies are reported separately and never counted as strict), failure rate (HTTP / invalid JSON),
verifier pass rate with 95% Wilson interval, verified facts per page, share of pages with a verified description,
injection compliance, p50/p95 latency, tokens per page and declared cost. A CSV review sheet is produced so a human can
check that verified facts are sensible (the verifier proves literalness, not usefulness).

Eligibility: valid JSON >= 90%, failures <= 10%, verifier pass >= 85%, zero injection compliance. Eligible models are
ranked by verified facts per page, verifier pass rate, p95 latency, then cost. Overlapping confidence intervals are
reported as statistical ties (30 pages cannot separate close models). The fallback is the best eligible model on a
different host.

## Candidates (config: `bench/models.json`)
IDs confirmed present in the NVIDIA catalog (`/v1/models`, 2026-10-03):
`deepseek-ai/deepseek-v4.1-flash`, `google/gemma-4-31b-it`, `openai/gpt-oss-20b`,
`nvidia/nemotron-3.5-lightning-30b-a3b`. Fallback: Gemini Flash-Lite via Google AI Studio (model id from
`GEMINI_FLASH_LITE_MODEL`, not verified here). The per-model "non-reasoning mode" switches in `extra_body` are
**unverified guesses**; an HTTP 400 in the results means they need adjusting. NVIDIA build prices are declared as $0
(free tier) and must be confirmed.

## How to run (needs keys and network)
    export NVIDIA_API_KEY=... GEMINI_API_KEY=... GEMINI_FLASH_LITE_MODEL=...
    uv run python scripts/model_benchmark.py corpus --count 30     # live Brreg + company sites; also reports how
                                                                    # often the identity gate verifies real sites
    uv run python scripts/model_benchmark.py run
    uv run python scripts/model_benchmark.py report --write BENCHMARK.md

## Until it has been run
The pipeline works without any LLM (deterministic extraction: meta description, emails, phones, linked social
profiles; the LLM only adds services and a description when a page has no meta description). Only the roughly 11% of
companies that list a website are affected, so the model choice changes cost and a few text fields, not the register
coverage that dominates the score. Choose the model by running the benchmark; do not pick one from this file.
