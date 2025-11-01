from __future__ import annotations

from fastapi import FastAPI, HTTPException, Body, Query
from pydantic import BaseModel
from pathlib import Path
from platformdirs import user_data_dir
from typing import Optional

from pm.core.models import EntryIn
from pm.core.services.vault_service import VaultService
from pm.core.crypto.passwords import generate_password

APP_DIR = Path(user_data_dir("PasswordManager"))
APP_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = APP_DIR / "vault.db"


class UnlockIn(BaseModel):
    master_password: str


class GenReq(BaseModel):
    length: int = 20
    upper: bool = True
    lower: bool = True
    digits: bool = True
    symbols: bool = True
    avoid_ambiguous: bool = True


def create_app() -> FastAPI:
    app = FastAPI(title="Password Manager API")
    state = {"vault": VaultService(DB_PATH)}

    @app.get("/api/health")
    def health():
        return {"ok": True}

    # ---- Auth / lifecycle ----------------------------------------------------
    @app.post("/api/setup")
    def setup(payload: UnlockIn = Body(..., description='{"master_password": "..."}')):
        v = state["vault"]
        if v.is_initialized():
            raise HTTPException(status_code=400, detail="already initialized")
        v.initialize(payload.master_password)
        return {"ok": True}

    @app.post("/api/unlock")
    def unlock(payload: UnlockIn = Body(..., description='{"master_password": "..."}')):
        v = state["vault"]
        try:
            v.unlock(payload.master_password)
            return {"ok": True}
        except RuntimeError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/api/lock")
    def lock():
        state["vault"].lock()
        return {"ok": True}

    # ---- Password utilities --------------------------------------------------
    @app.post("/api/password/generate")
    def password_generate(req: GenReq = Body(...)):
        try:
            pw = generate_password(
                length=req.length,
                upper=req.upper,
                lower=req.lower,
                digits=req.digits,
                symbols=req.symbols,
                avoid_ambiguous=req.avoid_ambiguous,
            )
            return {"password": pw}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # ---- Entries CRUD --------------------------------------------------------
    @app.get("/api/entries")
    def list_entries(q: Optional[str] = Query(None, description="Search query")):
        try:
            items = state["vault"].list(q=q)
            redacted = []
            for e in items:
                d = e.model_dump()
                d["password"] = None
                d["recovery_codes"] = None
                redacted.append(d)
            return {"items": redacted}
        except RuntimeError as e:
            raise HTTPException(status_code=401, detail=str(e))

    @app.post("/api/entries")
    def create_entry(
        e: EntryIn = Body(...),
        reveal: bool = Query(False, description="Include password & recovery_codes in response"),
    ):
        try:
            created = state["vault"].create(e)
            d = created.model_dump()
            if not reveal:
                d["password"] = None
                d["recovery_codes"] = None
            return {"item": d}
        except RuntimeError as e:
            raise HTTPException(status_code=401, detail=str(e))

    @app.get("/api/entries/{entry_id}")
    def get_entry(
        entry_id: str,
        reveal: bool = Query(False, description="Include password & recovery_codes in response"),
    ):
        try:
            ent = state["vault"].get(entry_id)
            if not ent:
                raise HTTPException(status_code=404, detail="not found")
            d = ent.model_dump()
            if not reveal:
                d["password"] = None
                d["recovery_codes"] = None
            return {"item": d}
        except RuntimeError as e:
            raise HTTPException(status_code=401, detail=str(e))

    @app.put("/api/entries/{entry_id}")
    def update_entry(
        entry_id: str,
        patch: EntryIn = Body(...),
        reveal: bool = Query(False, description="Include password & recovery_codes in response"),
    ):
        try:
            ent = state["vault"].update(entry_id, patch)
            if not ent:
                raise HTTPException(status_code=404, detail="not found")
            d = ent.model_dump()
            if not reveal:
                d["password"] = None
                d["recovery_codes"] = None
            return {"item": d}
        except RuntimeError as e:
            raise HTTPException(status_code=401, detail=str(e))

    @app.delete("/api/entries/{entry_id}")
    def delete_entry(entry_id: str):
        try:
            ok = state["vault"].delete(entry_id)
            if not ok:
                raise HTTPException(status_code=404, detail="not found")
            return {"ok": True}
        except RuntimeError as e:
            raise HTTPException(status_code=401, detail=str(e))

    return app


app = create_app()
