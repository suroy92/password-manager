from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import uuid4

def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

class EntryIn(BaseModel):
    title: str
    username: Optional[str] = None
    password: Optional[str] = None
    url: Optional[str] = None
    notes: Optional[str] = None
    recovery_codes: Optional[List[str]] = None

class Entry(EntryIn):
    id: str = Field(default_factory=lambda: uuid4().hex)
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    last_rotated_at: Optional[str] = None
