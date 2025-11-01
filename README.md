# Password Manager

Local‑first password manager with a **FastAPI** backend and a **React (MUI)** frontend. Current focus: a clean modern UI, solid CRUD for entries (with **recovery codes**), and a safe **password generator**. SQLCipher encryption and Google Drive sync are planned next.

<p align="left">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.120-009688?logo=fastapi&logoColor=white" />
  <img alt="React" src="https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black" />
  <img alt="MUI" src="https://img.shields.io/badge/MUI-6-007FFF?logo=mui&logoColor=white" />
  <img alt="Vite" src="https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white" />
  <img alt="License" src="https://img.shields.io/badge/License-TBD-lightgrey" />
</p>

---

## ✨ What’s implemented (current state)

**Backend (FastAPI)**
- Vault lifecycle: **setup**, **unlock**, **lock**
- **Entries** CRUD (title, username, password, url, notes, **recovery_codes[]**)
- **Password generator** (`/api/password/generate`) with options and ambiguity avoidance
- SQLite with sane pragmas; thread‑safe connection (`check_same_thread=False`)
- Secrets are **redacted by default**; opt‑in reveal via `?reveal=true`

**Frontend (React + Vite + MUI)**
- Pages: **Setup**, **Unlock**, **Vault**
- **Create/Edit** entry dialog
- **View secrets** dialog (👁️ show/hide password, copy password & codes)
- Password generator modal hooked to backend
- Graceful **empty state** and API error snackbars
- Vite dev proxy to backend → no CORS issues

---

## 📁 Project structure

```
Password Manager/
├─ pm/                       # Python package (backend)
│  ├─ api/
│  │  └─ main.py             # FastAPI app and routes
│  └─ core/
│     ├─ crypto/
│     │  └─ passwords.py     # Secure password generator
│     ├─ models.py           # Pydantic models (Entry, EntryIn)
│     ├─ persistence/
│     │  ├─ db.py            # SQLite (thread‑safe) + schema
│     │  └─ repository.py    # Data access
│     └─ services/
│        └─ vault_service.py # Vault lifecycle + business ops
├─ run_api.py                # Uvicorn launcher
├─ pyproject.toml            # Backend packaging (pip install -e .)
├─ .gitignore
├─ README.md                 # This file
└─ ui/                       # Frontend (Vite + React + MUI)
   ├─ package.json
   ├─ vite.config.ts         # Proxies /api to 127.0.0.1:8787 in dev
   └─ src/
      ├─ api.ts              # Typed API client (axios)
      ├─ types.ts            # Entry/EntryIn types
      ├─ theme.ts            # Dark theme
      ├─ routes.tsx          # Router
      ├─ components/
      │  ├─ AppLayout.tsx
      │  ├─ ConfirmDialog.tsx
      │  ├─ EntryDialog.tsx
      │  ├─ PasswordGenDialog.tsx
      │  └─ ViewSecretsDialog.tsx   # 👁️ view/copy secrets
      └─ pages/
         ├─ Setup.tsx
         ├─ Unlock.tsx
         └─ Vault.tsx
```

---

## ✅ Prerequisites

- **Python** ≥ 3.10
- **Node.js** ≥ 18 and **npm**
- Windows, macOS, or Linux

---

## 🚀 Quick start

### 1) Backend

```bash
# from repo root
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -e .
python run_api.py   # serves on http://127.0.0.1:8787
```

> Vault database location (Windows):  
> `%LOCALAPPDATA%\PasswordManager\vault.db`  
> Created via `platformdirs.user_data_dir("PasswordManager")`.

### 2) Frontend

```bash
# in another terminal
cd ui
npm install
npm run dev          # http://localhost:5173 (proxying /api to 127.0.0.1:8787)
```

---

## 🧭 Using the app

### First run (Setup → Unlock → Vault)

1. Open `http://localhost:5173`.
2. Go to **Setup** and create a **master password**.
3. Use **Unlock** with the same password.
4. Navigate to **Vault** to create your first entry.

### Working with entries

- **New/Edit**: click **New** or the ✏️ (edit) icon.  
  - You can **generate a secure password** inside the dialog.  
  - **Recovery codes**: paste one per line.
- **View secrets**: click the 👁️ eye icon in the table row.  
  - Show/hide password, copy password and codes quickly.
- **Delete**: click the 🗑 icon (confirmation required).

---

## 🔌 API reference (brief)

Base URL (dev): `http://127.0.0.1:8787/api`  
OpenAPI docs: `http://127.0.0.1:8787/docs`

### Health

```
GET /api/health
→ { "ok": true }
```

### Vault lifecycle

```
POST /api/setup
Body: { "master_password": "..." }
→ { "ok": true }   # 400 if already initialized
```

```
POST /api/unlock
Body: { "master_password": "..." }
→ { "ok": true }   # 400 if not initialized or wrong password
```

```
POST /api/lock
→ { "ok": true }
```

### Password generator

```
POST /api/password/generate
Body (all optional with defaults):
{
  "length": 20,
  "upper": true,
  "lower": true,
  "digits": true,
  "symbols": true,
  "avoid_ambiguous": true
}
→ { "password": "generated-string" }
```

### Entries
> Secrets are **redacted by default**. Use `?reveal=true` to include `password` and `recovery_codes`.

```
GET /api/entries?q=<optional>
→ { "items": [ { id, title, username, url, notes, created_at, updated_at, ... } ] }
```

```
POST /api/entries?reveal=true
Body: {
  "title": "GitHub",
  "username": "octo@example.com",
  "password": "…",
  "url": "https://github.com",
  "notes": "personal",
  "recovery_codes": ["ABCD-EFGH", "IJKL-MNOP"]
}
→ { "item": { ... possibly with password/recovery_codes if reveal=true } }
```

```
GET /api/entries/{id}?reveal=true
→ { "item": { ... } }   # 404 if missing
```

```
PUT /api/entries/{id}?reveal=false
Body: same as POST (fields optional)
→ { "item": { ... } }
```

```
DELETE /api/entries/{id}
→ { "ok": true }  # 404 if missing
```

---

## 🔐 Security notes (current)

- DB is **unencrypted SQLite** for now; **SQLCipher** is the next milestone.
- Secrets are **redacted** in list/read responses unless `reveal=true` is explicitly provided.
- Password generator uses `secrets` and guarantees at least one char from each selected class; ambiguous characters can be excluded.

---

## 🏗️ Production build (UI)

```bash
cd ui
npm run build
npm run preview  # simple preview server (not for public internet)
```

For a desktop build with **pywebview**, we’ll later serve the compiled `ui/dist` locally from the Python app and point the webview to it.

---

## 🛠️ Troubleshooting

**422 Unprocessable Content on /api/setup or /api/unlock**  
Ensure the body is **raw JSON** with the exact key:
```json
{ "master_password": "YourStrongMasterPass" }
```
(We made the FastAPI body parsing explicit to avoid this in most clients.)

**500 with “SQLite objects created in a thread…”**  
We’ve set `check_same_thread=False` and WAL mode in `pm/core/persistence/db.py`. Make sure your local file matches that configuration and restart.

**UI loads but shows an error / empty table**  
- If the vault is **locked**, API returns 401; the UI will show a Snackbar. Unlock from the **Unlock** page.
- If there are **no entries**, you’ll see a friendly empty state—click **New**.

**Port conflict**  
- Backend: change `port` in `run_api.py`.
- Frontend: change `server.port` in `ui/vite.config.ts`.

---

## 🧭 Roadmap (near‑term)

1. App **session** endpoint + UI 401 interceptor → auto‑redirect to Unlock.  
2. **SQLCipher** vault with master‑password‑derived key + migration script.  
3. **Google Drive** sync (AppData folder, atomic writes, conflict resolution).  
4. **60‑day rotation reminders** (`last_rotated_at`) + UI banner.  
5. **Leak alerts** via k‑Anonymity (HIBP) as an opt‑in check.  
6. **Auto‑lock on idle** and **clipboard auto‑clear**.

---

## 📜 License

TBD.
