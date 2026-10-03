.PHONY: install test lint run smoke sample bench bench-models batch audit
export PYTHONPATH := src:kit/src
PY ?= uv run python

install:
	uv sync --python 3.12

test:
	uv run pytest -q

lint:
	uv run ruff check src tests

# make run INPUT=companies.jsonl OUT=out/ [BULK=brreg-enheter.csv]
run:
	$(PY) run_agent.py run --organisations "$(INPUT)" --out "$(OUT)" $(if $(BULK),--bulk "$(BULK)",)

# make sample  -> samples/{submission,daily,dev}.jsonl (seeded, reproducible)
sample:
	$(PY) -m signalpost.sample --universe data/orgs.json --out samples

# make bench -> 100-company daily-test benchmark (time, requests, cost vs limits); add RERUN=1 for refresh run
bench:
	$(PY) scripts/benchmark.py $(if $(RERUN),--rerun,)

# LLM model benchmark (needs keys + network): make bench-models  -> BENCHMARK.md
bench-models:
	$(PY) scripts/model_benchmark.py corpus --count 30
	$(PY) scripts/model_benchmark.py run
	$(PY) scripts/model_benchmark.py report

# make batch BULK=brreg-enheter.csv.gz  -> 1,500 seeded profiles in out/profiles.jsonl (local scale test, not submitted)
batch:
	REQUEST_BUDGET_TOTAL=$${REQUEST_BUDGET_TOTAL:-6000} $(PY) run_agent.py run --organisations samples/submission.jsonl --out out/batch $(if $(BULK),--bulk "$(BULK)",) --bulk-register on --run-id batch
	cp out/batch/envelopes.jsonl out/profiles.jsonl

# make audit -> wrong-company audit of out/profiles.jsonl + 50-profile human review sheet (out/audit/)
audit:
	$(PY) scripts/audit_sample.py --profiles out/profiles.jsonl --out out/audit
