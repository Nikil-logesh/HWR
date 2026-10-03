"""Read the batch input (JSON list / JSONL / text) and the registry rows used as free identity fallback."""
from __future__ import annotations

import csv
import gzip
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .universe import valid_orgnr


@dataclass
class InputRow:
    raw: str
    org: str  # digits only
    valid: bool
    extra: dict[str, Any] = field(default_factory=dict)


def _org_of(value: Any) -> str:
    if isinstance(value, dict):
        for k in ("organisation_number", "organisasjonsnummer", "orgnr", "org_number", "id"):
            if value.get(k) is not None:
                return str(value[k])
        return ""
    return str(value)


def read_inputs(path: str | Path) -> list[InputRow]:
    """Never raises on a bad id: a malformed number still becomes a row so it gets a terminal envelope."""
    p = Path(path)
    with (gzip.open(p, "rt", encoding="utf-8") if p.suffix == ".gz" else p.open(encoding="utf-8")) as fh:
        text = fh.read()
    stripped = text.lstrip()
    values: list[Any]
    if stripped.startswith("["):
        values = json.loads(text)
    elif stripped.startswith("{") and "\n" not in stripped.strip():
        body = json.loads(text)
        values = body.get("organisation_numbers", [body]) if isinstance(body, dict) else body
    elif stripped.startswith("{"):
        values = [json.loads(ln) for ln in text.splitlines() if ln.strip()]
    else:
        values = [ln.strip() for ln in text.splitlines() if ln.strip()]
    rows: list[InputRow] = []
    seen: set[str] = set()
    for v in values:
        raw = _org_of(v)
        digits = re.sub(r"\D", "", raw)
        key = digits or raw
        if key in seen:  # exactly one envelope per distinct input id
            continue
        seen.add(key)
        extra = {k: x for k, x in v.items() if k in ("evaluation_split", "sample_slice")} if isinstance(v, dict) else {}
        rows.append(InputRow(raw=raw, org=digits, valid=valid_orgnr(digits), extra=extra))
    return rows


_BOOL = {"true": True, "false": False}
_KEY_FIX = {"registrertIMvaRegisteret": "registrertIMvaregisteret",
            "registreringsdatoenhetsregisteret": "registreringsdatoEnhetsregisteret"}
_INTS = {"antallAnsatte"}


def csv_row_to_entity(row: dict[str, str]) -> dict[str, Any]:
    """Unflatten a Brreg bulk-CSV row (dotted columns) into the nested shape of /enheter/{org} JSON, so the
    same claim extractor serves both. Empty cells are dropped; booleans/ints/decimals are typed."""
    out: dict[str, Any] = {}
    for key, raw in row.items():
        if not isinstance(key, str) or not isinstance(raw, str) or raw == "":
            continue  # malformed row (extra fields land under a None key as a list): ignore, never crash
        key = _KEY_FIX.get(key, key)
        val: Any = _BOOL.get(raw.lower(), raw)
        if key in _INTS and raw.lstrip("-").isdigit():
            val = int(raw)
        elif key.endswith(".adresse"):  # CSV joins address lines with a newline; the JSON API gives a list
            val = [ln.strip() for ln in raw.split("\n") if ln.strip()]
        elif key == "kapital.belop":
            try:
                val = float(raw)
            except ValueError:
                pass
        node = out
        parts = key.split(".")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = val
    return out


def _open_text(path: Path):
    """Open by CONTENT, not extension: the Brreg bulk download is gzip even when saved as `.csv` (as the kit's
    README does). Handles a UTF-8 BOM."""
    with path.open("rb") as fh:
        magic = fh.read(2)
    if magic == b"\x1f\x8b":
        return gzip.open(path, "rt", encoding="utf-8-sig", newline="")
    return path.open(encoding="utf-8-sig", newline="")


def load_registry_rows(path: str | Path | None, wanted: set[str]) -> dict[str, dict[str, Any]]:
    """Stream the Brreg bulk CSV (any delimiter, gzip or plain) or the universe JSONL and keep only the wanted
    organisation numbers. A Git LFS pointer or unreadable file yields {} with a warning (never a crash)."""
    if not path or not Path(path).exists() or not wanted:
        return {}
    p = Path(path)
    found: dict[str, dict[str, Any]] = {}
    try:
        with _open_text(p) as fh:
            head = fh.read(8192)
            fh.seek(0)
            if head.startswith("version https://git-lfs"):
                raise RuntimeError(f"{p} is a Git LFS pointer, not data")
            if head.lstrip().startswith("{"):  # JSONL universe
                for ln in fh:
                    if not ln.strip():
                        continue
                    row = json.loads(ln)
                    org = row.get("organisation_number")
                    if org in wanted:
                        found[org] = row
                        if len(found) == len(wanted):
                            break
                return found
            from norway_company_agent.sampling import normalize_row
            # Delimiter from the header line, standard quoting. (csv.Sniffer guessed doublequote=False on the real
            # file and mis-parsed every row containing an escaped quote.)
            header = head.split("\n", 1)[0]
            delim = max(",;\t", key=header.count)
            for row in csv.DictReader(fh, delimiter=delim):
                org = row.get("organisasjonsnummer") or row.get("Organisasjonsnummer")
                if org in wanted:
                    n = normalize_row(row)
                    n.pop("raw", None)
                    n["_entity"] = csv_row_to_entity(row)  # full record: entity module runs at 0 requests
                    found[org] = n
                    if len(found) == len(wanted):
                        break
    except (RuntimeError, OSError, UnicodeDecodeError, ValueError) as exc:
        import sys
        print(f"warning: registry file {p} unusable ({type(exc).__name__}: {exc}); "
              "continuing without the free register fallback", file=sys.stderr)
        return {}
    return found
