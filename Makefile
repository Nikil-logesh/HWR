.PHONY: install test lint run smoke sample bench
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
