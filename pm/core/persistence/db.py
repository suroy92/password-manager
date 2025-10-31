from __future__ import annotations
from pathlib import Path
from typing import Optional
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS entries (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  username TEXT,
  password TEXT,
  url TEXT,
  notes TEXT,
  recovery_codes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  last_rotated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_entries_updated_at ON entries(updated_at);
"""

class Database:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.con: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.con = sqlite3.connect(str(self.path))
        self.con.execute("PRAGMA foreign_keys = ON;")
        self.con.executescript(SCHEMA)
        self.con.commit()

    def close(self) -> None:
        if self.con:
            self.con.close()
            self.con = None
