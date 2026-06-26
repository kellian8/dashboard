"""Local SQLite store of total-value snapshots.

The endpoint does not provide "Last 24h" or "ROR", so we persist a timestamped
total-value series and derive those by comparing against the row nearest to
24 hours ago.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

from loguru import logger

from ..paths import DB_PATH


class SnapshotStore:
    def __init__(self, db_path=DB_PATH) -> None:
        self._db_path = db_path
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def _ensure_schema(self) -> None:
        logger.debug("Ensuring snapshot schema at {}", self._db_path)
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS snapshots ("
                "id INTEGER PRIMARY KEY, ts TEXT NOT NULL, total_value REAL NOT NULL)"
            )

    def insert(self, ts: datetime, total_value: float) -> None:
        logger.debug("Inserting snapshot | ts={} value={:.2f}", ts.isoformat(), total_value)
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO snapshots (ts, total_value) VALUES (?, ?)",
                (ts.isoformat(), total_value),
            )
            cutoff = (ts - timedelta(days=7)).isoformat()
            conn.execute("DELETE FROM snapshots WHERE ts < ?", (cutoff,))

    def value_near_24h_ago(self) -> float | None:
        """Total value of the snapshot closest to 24h ago, or None if empty."""
        target = (datetime.now(tz=timezone.utc) - timedelta(hours=24)).isoformat()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT total_value FROM snapshots "
                "ORDER BY ABS(JULIANDAY(ts) - JULIANDAY(?)) LIMIT 1",
                (target,),
            ).fetchone()
        baseline = row[0] if row else None
        if baseline is None:
            logger.debug("No 24h baseline available yet")
        else:
            logger.debug("24h baseline: {:.2f}", baseline)
        return baseline
