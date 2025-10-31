
from fastapi import APIRouter, HTTPException

router = APIRouter()

STATE = {
    "unlocked": False,
    "entries": [
        {"id": "1", "title": "GitHub", "username": "octo@example.com", "url": "https://github.com", "notes": "", "updated_at": "2025-10-01T12:00:00Z"},
        {"id": "2", "title": "Gmail", "username": "user@gmail.com", "url": "https://mail.google.com", "notes": "2FA enabled", "updated_at": "2025-10-10T09:30:00Z"},
    ],
}

@router.post("/unlock")
def unlock(payload: dict):
    if not payload.get("master_password"):
        raise HTTPException(status_code=400, detail="master_password required")
    STATE["unlocked"] = True
    return {"ok": True}

@router.get("/entries")
def list_entries(q: str | None = None):
    if not STATE["unlocked"]:
        raise HTTPException(status_code=401, detail="locked")
    data = STATE["entries"]
    if q:
        ql = q.lower()
        data = [e for e in data if ql in e["title"].lower() or ql in (e.get("username") or "").lower()]
    return {"items": data}
