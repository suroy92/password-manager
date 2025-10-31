from __future__ import annotations
from typing import Iterable, Optional, Tuple, List
from .db import Database
from ..models import Entry, EntryIn
from datetime import datetime
import json


def _dump_codes(codes: Optional[List[str]]) -> Optional[str]:
    if codes is None:
        return None
    return json.dumps(codes, ensure_ascii=False)


def _load_codes(s: Optional[str]) -> Optional[List[str]]:
    if s is None:
        return None
    try:
        return json.loads(s)
    except Exception:
        return None


class Repository:
    def __init__(self, db: Database):
        if db.con is None:
            raise RuntimeError("DB not connected")
        self.db = db

    def get_meta(self, key: str) -> Optional[str]:
        cur = self.db.con.execute("SELECT value FROM meta WHERE key=?", (key,))
        row = cur.fetchone()
        return row[0] if row else None

    def set_meta(self, key: str, value: str) -> None:
        self.db.con.execute(
            "INSERT INTO meta(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
        self.db.con.commit()

    def list_entries(self, q: Optional[str] = None) -> Iterable[Entry]:
        sql = "SELECT id,title,username,password,url,notes,recovery_codes,created_at,updated_at,last_rotated_at FROM entries"
        params: Tuple = ()
        if q:
            sql += " WHERE LOWER(title) LIKE ? OR LOWER(username) LIKE ?"
            like = f"%{q.lower()}%"
            params = (like, like)
        sql += " ORDER BY updated_at DESC"
        cur = self.db.con.execute(sql, params)
        for r in cur.fetchall():
            yield Entry(
                id=r[0], title=r[1], username=r[2], password=r[3], url=r[4], notes=r[5],
                recovery_codes=_load_codes(r[6]), created_at=r[7], updated_at=r[8], last_rotated_at=r[9]
            )

    def get_entry(self, entry_id: str) -> Optional[Entry]:
        cur = self.db.con.execute(
            "SELECT id,title,username,password,url,notes,recovery_codes,created_at,updated_at,last_rotated_at FROM entries WHERE id=?",
            (entry_id,),
        )
        r = cur.fetchone()
        if not r:
            return None
        return Entry(
            id=r[0], title=r[1], username=r[2], password=r[3], url=r[4], notes=r[5],
            recovery_codes=_load_codes(r[6]), created_at=r[7], updated_at=r[8], last_rotated_at=r[9]
        )

    def create_entry(self, e: Entry) -> Entry:
        self.db.con.execute(
            "INSERT INTO entries(id,title,username,password,url,notes,recovery_codes,created_at,updated_at,last_rotated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (e.id, e.title, e.username, e.password, e.url, e.notes, _dump_codes(e.recovery_codes), e.created_at, e.updated_at, e.last_rotated_at),
        )
        self.db.con.commit()
        return e

    def update_entry(self, entry_id: str, patch: EntryIn) -> Optional[Entry]:
        cur = self.get_entry(entry_id)
        if not cur:
            return None
        updated = cur.model_copy(update=patch.model_dump(exclude_unset=True))
        updated.updated_at = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        self.db.con.execute(
            "UPDATE entries SET title=?, username=?, password=?, url=?, notes=?, recovery_codes=?, updated_at=?, last_rotated_at=? WHERE id=?",
            (updated.title, updated.username, updated.password, updated.url, updated.notes, _dump_codes(updated.recovery_codes), updated.updated_at, updated.last_rotated_at, entry_id),
        )
        self.db.con.commit()
        return updated

    def delete_entry(self, entry_id: str) -> bool:
        cur = self.db.con.execute("DELETE FROM entries WHERE id=?", (entry_id,))
        self.db.con.commit()
        return cur.rowcount > 0
