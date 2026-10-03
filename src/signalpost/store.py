"""SQLite snapshot store: every distinct profile state is preserved; identical reruns add no duplicate rows."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
from pathlib import Path

from .models import Envelope


def state_hash(env: Envelope) -> str:
    """Hash of what the profile SAYS (claims minus observation timestamps/confidence), not of run metadata."""
    rows = sorted(
        (c.field, c.reporting_period or "", c.availability, json.dumps(c.value, sort_keys=True, ensure_ascii=False))
        for c in env.claims)
    return hashlib.sha256(json.dumps(rows, ensure_ascii=False).encode()).hexdigest()


class SnapshotStore:
    def __init__(self, path: str | Path = ":memory:"):
        self._db = sqlite3.connect(str(path), check_same_thread=False)
        self._lock = threading.Lock()
        self._db.executescript("""
        CREATE TABLE IF NOT EXISTS snapshots(
          id INTEGER PRIMARY KEY AUTOINCREMENT, org TEXT NOT NULL, run_id TEXT NOT NULL, saved_at TEXT NOT NULL,
          state_hash TEXT NOT NULL, envelope TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS snap_org ON snapshots(org, id);
        CREATE TABLE IF NOT EXISTS web_state(org TEXT PRIMARY KEY, homepage_sha TEXT, homepage_url TEXT);
        """)

    def latest(self, org: str) -> Envelope | None:
        with self._lock:
            row = self._db.execute("SELECT envelope FROM snapshots WHERE org=? ORDER BY id DESC LIMIT 1",
                                   (org,)).fetchone()
        return Envelope.model_validate_json(row[0]) if row else None

    def history(self, org: str) -> list[Envelope]:
        with self._lock:
            rows = self._db.execute("SELECT envelope FROM snapshots WHERE org=? ORDER BY id", (org,)).fetchall()
        return [Envelope.model_validate_json(r[0]) for r in rows]

    def save(self, env: Envelope) -> bool:
        """Persist. Returns True if a NEW snapshot row was added. If the profile state equals the latest
        snapshot, the latest row is updated in place (fresh check dates) and nothing is duplicated."""
        h = state_hash(env)
        with self._lock:
            last = self._db.execute("SELECT id, state_hash FROM snapshots WHERE org=? ORDER BY id DESC LIMIT 1",
                                    (env.organisation_number,)).fetchone()
            if last and last[1] == h:
                self._db.execute("UPDATE snapshots SET envelope=?, run_id=?, saved_at=? WHERE id=?",
                                 (env.to_json_line(), env.run.run_id, env.run.completed_at, last[0]))
                self._db.commit()
                return False
            self._db.execute("INSERT INTO snapshots(org, run_id, saved_at, state_hash, envelope) VALUES(?,?,?,?,?)",
                             (env.organisation_number, env.run.run_id, env.run.completed_at, h, env.to_json_line()))
            self._db.commit()
            return True

    def get_web_state(self, org: str) -> tuple[str | None, str | None]:
        with self._lock:
            row = self._db.execute("SELECT homepage_sha, homepage_url FROM web_state WHERE org=?", (org,)).fetchone()
        return (row[0], row[1]) if row else (None, None)

    def set_web_state(self, org: str, sha: str | None, url: str | None) -> None:
        with self._lock:
            self._db.execute("REPLACE INTO web_state VALUES(?,?,?)", (org, sha, url))
            self._db.commit()
