"""Signalpost agent. Reuses the Builderr reference kit (kit/src) as a library."""
import sys
from pathlib import Path

_KIT_SRC = Path(__file__).resolve().parents[2] / "kit" / "src"
if _KIT_SRC.is_dir() and str(_KIT_SRC) not in sys.path:
    sys.path.insert(0, str(_KIT_SRC))

__version__ = "0.1.0"
