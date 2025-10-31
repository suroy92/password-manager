from __future__ import annotations
from pathlib import Path
from typing import Optional, Iterable
from ..models import Entry, EntryIn
from ..persistence.db import Database
from ..persistence.repository import Repository

class VaultService:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self._db: Optional[Database] = None
        self._repo: Optional[Repository] = None
        self._unlocked: bool = False

    def is_initialized(self) -> bool:
        return self.db_path.exists()

    def initialize(self, master_password: str) -> None:
        db = Database(self.db_path)
        db.connect()
        repo = Repository(db)
        db.close()

    def unlock(self, master_password: str) -> None:
        db = Database(self.db_path)
        if not db.path.exists():
            raise RuntimeError("vault not initialized")
        db.connect()
        repo = Repository(db)
        self._db, self._repo = db, repo
        self._unlocked = True

    def lock(self) -> None:
        if self._db:
            self._db.close()
        self._db = None
        self._repo = None
        self._unlocked = False

    def list(self, q: Optional[str] = None) -> Iterable[Entry]:
        self._ensure_unlocked()
        return list(self._repo.list_entries(q=q))

    def get(self, entry_id: str) -> Optional[Entry]:
        self._ensure_unlocked()
        return self._repo.get_entry(entry_id)

    def create(self, e: EntryIn) -> Entry:
        self._ensure_unlocked()
        ent = Entry(**e.model_dump())
        return self._repo.create_entry(ent)

    def update(self, entry_id: str, patch: EntryIn) -> Optional[Entry]:
        self._ensure_unlocked()
        return self._repo.update_entry(entry_id, patch)

    def delete(self, entry_id: str) -> bool:
        self._ensure_unlocked()
        return self._repo.delete_entry(entry_id)

    def _ensure_unlocked(self) -> None:
        if not self._unlocked or self._repo is None:
            raise RuntimeError("vault locked")
