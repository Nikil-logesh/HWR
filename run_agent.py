#!/usr/bin/env python3
"""Single entry point:  uv run python run_agent.py run --organisations FILE --out DIR  (see --help)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "kit" / "src")]

from signalpost.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
