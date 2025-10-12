Absolutely—here’s the **complete README.md** ready to copy-paste.

````markdown
# 🔐 Password Manager

A simple yet secure **Password Manager** built with **Python** and **Tkinter**.  
Passwords are encrypted at rest using keys derived from a **master password** (Argon2id KDF), and stored in a local **SQLite** database. The desktop UI is modernized with **ttkbootstrap** and a classic menubar.

---

## 🚀 Features

- ✅ **Encrypted storage** (Fernet; key derived from master password via Argon2id; per-vault salt + canary)
- ✅ **Store / View / Update / Delete** entries
- ✅ **Search** bar with live filtering (title/username)
- ✅ **Sortable** columns & **row striping**
- ✅ **Show/Hide** password & **strength meter** in dialogs
- ✅ **Copy to clipboard** with auto-clear
- ✅ **Encrypted Export** (`.pmjson.enc`) and optional **plaintext export** (for backup/migration)
- ✅ **Classic Menubar** (File & Security)
- ✅ **Global font** tuned for readability (Windows prefers **Inter**; falls back to system UI fonts)

> **Security tip:** plaintext exports are for temporary migration/backups only. Prefer encrypted exports.

---

## 🛠️ Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/<your-username>/Password-Manager.git
cd Password-Manager
````

### 2️⃣ Create and activate a virtual environment (optional)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` should include:

```
cryptography
ttkbootstrap
```

Tkinter ships with most Python distributions. If missing, install it via your OS package manager.

---

## ▶️ Running the Application

```bash
python main.py
```

* **First run:** you’ll be prompted to set a **master password**. Keep this safe; it cannot be recovered.
* **Migrating from legacy `secret.key`:** export your old entries (plaintext JSON), then import/rewrap in the new vault. After migration, the legacy `secret.key` is no longer used.

---

## 🧰 Usage Guide

### Menubar

* **File → Store New**
  Add a new entry (title, username, password, optional recovery codes). Includes a strength meter and a show/hide toggle.

* **File → Generate Password**
  Create strong passwords (length + include numbers/symbols).

* **File → Export (Encrypted)…**
  Creates a portable, encrypted export (`.pmjson.enc`). You can protect it with a separate passphrase or your master password.

* **File → Export (Plaintext)…**
  Writes `Exported.json` for migration/backups. Delete after use.

* **File → Exit**
  Close the application.

* **Security → Change Master Password…**
  Safely re-encrypts all secrets under a new key (rotates salt + canary).

### Table & Search

* Use the **Search** field above the table to filter by **title** or **username**.
* Click column headers to **sort**.
* **Double-click** a row to view details.
* **Right-click** a row for quick actions (View, Copy, Update, Delete).

### Keyboard Shortcuts

* `Ctrl+N` — Store New
* `Ctrl+G` — Generate Password
* `Ctrl+E` — Export (Plaintext)
* `Ctrl+Shift+E` — Export (Encrypted)

---

## 🔒 Security Model (Phase-1)

* **Master password** is never stored. A key is derived via **Argon2id** (scrypt fallback supported) with a per-vault **salt** and validated using a **canary**.
* **Clipboard auto-clear** for copied passwords.
* **Encrypted export** (`.pmjson.enc`) can be decrypted by the app (or a small helper script) using the chosen passphrase or the vault key (depending on mode).

> If you forget the master password and have **no encrypted export** or plaintext backup, the data is intentionally unrecoverable.

---

## 📂 Project Structure

```
Password-Manager/
├── main.py                     # Tkinter UI (ttkbootstrap), menubar, dialogs, search
├── database.py                 # SQLite operations
├── encryption.py               # Vault init/unlock; password generator; glue into pm_core
├── pm_core/
│   ├── __init__.py
│   ├── kdf.py                  # Argon2id/scrypt derivation
│   ├── settings_store.py       # settings/schema_migrations tables, canary/salt helpers
│   ├── vault_crypto.py         # Fernet wrapper
│   ├── export_import.py        # Encrypted export helpers
│   ├── rotation.py             # Master password rotation (re-wrap secrets)
│   ├── clipboard.py            # Clipboard auto-clear
│   ├── logging_setup.py        # Redacted rotating logger (optional)
│   └── migration.py            # Legacy migration helpers (if needed)
│
├── requirements.txt            # Dependencies (cryptography, ttkbootstrap, ...)
├── LICENSE
├── README.md
├── CHANGELOG.md
│
├── passwords.db                # SQLite DB (created at runtime)
└── Exported.json               # Optional plaintext export (created on demand)
```

---

## ⚙️ Technical Overview

* **Language:** Python 3.10+
* **GUI:** Tkinter + ttkbootstrap
* **DB:** SQLite
* **Crypto:** `cryptography` (Fernet); keys via Argon2id (salted); per-vault canary
* **Exports:** Encrypted `.pmjson.enc` (recommended) + optional plaintext JSON
* **Fonts:** Global font set at startup with platform-aware fallbacks (Windows prefers **Inter**)

---

## 🧑‍💻 Contributing

1. Fork the repo
2. Create a feature branch (`feature/your-feature`)
3. Commit and push
4. Open a PR

---

## 📜 License

This project is licensed under the **MIT License**. See [LICENSE](./LICENSE).