.PHONY: install test lint run smoke sample
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
	$(PY) -m signalpost.cli run --organisations "$(INPUT)" --out "$(OUT)" $(if $(BULK),--bulk "$(BULK)",)

# make sample  -> samples/{submission,daily,dev}.jsonl (seeded, reproducible)
sample:
	$(PY) -m signalpost.sample --universe data/orgs.json --out samples
