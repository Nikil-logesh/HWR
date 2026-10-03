# Model benchmark

Run: 2026-10-03 05:54 UTC | corpus: 30 items (register_text_proxy) + 3 synthetic prompt-injection probes | prompt and schema identical for every model | temperature 0.

Task: given already-fetched, identity-verified page text, propose a one-sentence description and up to six services as VERBATIM text. A code verifier keeps a fact only if its evidence snippet occurs in the page and contains the value. Financial values and identity are never delegated to a model.

| model | host | strict JSON | valid after recovery | failures | verifier pass (95% CI) | verified facts/page | pages with description | injection followed | p50 / p95 latency (s) | tokens/page | cost USD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| nemotron-3.5-lightning-30b-a3b (`nvidia/nemotron-3.5-lightning-30b-a3b`) | integrate.api.nvidia.com | 0.73 | 0.73 | 0.27 | 0.96 (0.90-0.99) | 2.73 | 0.53 | 0/3 | 4.59 / 16.72 | 556 | 0.0 |
| gemma-4-31b-it (`google/gemma-4-31b-it`) | integrate.api.nvidia.com | 0.90 | 0.90 | 0.10 | 1.00 (0.95-1.00) | 2.47 | 0.90 | 0/3 | 14.35 / 28.82 | 481 | 0.0 |
| gpt-oss-20b (`openai/gpt-oss-20b`) | integrate.api.nvidia.com | 1.00 | 1.00 | 0.00 | 1.00 (0.94-1.00) | 2.17 | 1.00 | 1/3 | 3.60 / 13.98 | 664 | 0.0 |

> **Corpus caveat:** Real company-authored Norwegian text (registered purpose/activity from the Brreg bulk CSV) wrapped in synthetic page boilerplate. Not real website HTML: yields on real sites may differ.

## Recommendation

Eligibility: valid JSON >= 90%, failures <= 10%, verifier pass >= 85%, zero injection compliance. Eligible models are ranked by verified facts per page, then verifier pass rate, then p95 latency, then cost.

- **Primary:** `gemma-4-31b-it`
- **Fallback:** none: no second model met the eligibility thresholds

## Dropped-fact reasons (real pages)

- gemma-4-31b-it: {}; errors: {"ReadTimeout": 4}
- gpt-oss-20b: {}; errors: {}
- nemotron-3.5-lightning-30b-a3b: {"snippet does not contain value": 3}; errors: {"invalid_json": 3, "ReadTimeout": 7}

## Run conditions (read before interpreting)
* Three models were run **concurrently** (one process each) against the NVIDIA build free tier, 1 repeat, temperature 0,
  client timeout 40 s, one retry on 429/5xx. Timeouts count as failures. The free endpoint's latency is variable and
  my own parallel load may have inflated it; timeouts were not retried.
* Corpus: 30 items of real company-authored Norwegian text (registered purpose/activity from the Brreg bulk CSV) in synthetic
  page boilerplate + 3 synthetic injection probes. **Not real website HTML**; a run on real pages (`corpus --source web`)
  is still needed. 30 pages and 3 probes are small samples (see the confidence intervals).
* `deepseek-ai/deepseek-v4.1-flash` was **excluded**: 3 probe calls and 2 retries of a trivial "Say OK" request (50 s and
  170 s timeouts) all timed out. It may be a temporary free-tier problem; re-test before dropping it for good.
* Gemini Flash-Lite was **not run** (no Google key).
* The eligibility thresholds are those fixed in `modelbench.py` before the run; they were not changed after seeing results.

## Interpretation (written by hand after the run; the numbers above are computed)
* **The verifier did its job.** No model passed a fabricated fact: the three facts Nemotron proposed whose snippet did not contain
  the value were dropped. Because every kept fact is literal page text, the model choice affects how many facts we get and what
  they cost, not whether published facts are true.
* **gemma-4-31b-it** is the only eligible model, but only just: its 10% failure rate is exactly at the threshold (4 timeouts of
  33 at the 40 s limit) and its median call takes 14 s. Quality when it answers is the best here (verifier 100%, descriptions on
  90% of pages, resisted all 3 injections).
* **gpt-oss-20b** was the most reliable and fastest (100% strict JSON, 0 failures, median 3.6 s) but **followed 1 of 3
  prompt injections** and is therefore ineligible under the zero-compliance rule. The injected "service" passed the verifier
  because the instruction text really is on the page: the literal-snippet check cannot stop injection by itself.
  A deterministic filter that drops candidates whose snippet contains instruction-like text (not yet implemented) would bound
  the harm and allow measuring end-to-end leakage separately from model compliance; adding it, and then changing the rule, would
  be a post-hoc decision and must be reported as such.
* **nemotron-3.5-lightning-30b-a3b** with `enable_thinking: false` (a guess that worked) was fast when it answered but failed
  27% of calls (7 timeouts, 3 invalid JSON): ineligible.
* No recommendation is made for a fallback: only one model met the thresholds. The configured fallback (Gemini Flash-Lite)
  is unmeasured.
* Impact is small either way: only the ~11% of companies that list a website call a model at all, and the pipeline keeps working
  with deterministic extraction when a call fails.

## Reproduce
    export NVIDIA_API_KEY=...        # never commit it
    uv run python scripts/model_benchmark.py corpus --source register-text --csv brreg-enheter.csv.gz --count 30
    for m in gemma-4-31b-it gpt-oss-20b nemotron-3.5-lightning-30b-a3b; do
      uv run python scripts/model_benchmark.py run --only $m --out bench/results/proxy-$m & done; wait
    uv run python scripts/model_benchmark.py report --results bench/results/proxy-gemma-4-31b-it,bench/results/proxy-gpt-oss-20b,bench/results/proxy-nemotron-3.5-lightning-30b-a3b
Raw per-call rows (`bench/results/*/rows.jsonl`) and the human review sheet (`review_sheet.csv`) are git-ignored; the table above
is computed from them.
