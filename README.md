# 🔐 Password Manager (Python + Tkinter)

A simple yet secure **Password Manager** built using **Python, Tkinter, SQLite, and Fernet Encryption**.
This desktop app allows you to **store, view, update, delete, copy, and export passwords** — all encrypted locally.

---

## 🚀 Features

* ✅ Add & store passwords securely (AES encryption using the `cryptography` library)
* ✅ Generate strong passwords (customizable length, with numbers & symbols)
* ✅ View and update saved entries
* ✅ Copy password to clipboard with one click
* ✅ Delete entries with confirmation
* ✅ Export passwords to JSON
* ✅ Local SQLite storage — works completely offline
* ✅ Clean, modern Tkinter-based UI
* ✅ Automatic encryption key generation and handling

---

## 🧩 Project Structure

```
Password-Manager/
│
├── main.py            # Main GUI application
├── database.py        # Database logic and CRUD operations
├── encryption.py      # Encryption & password generation utilities
├── passwords.db       # (Auto-created) SQLite database file
├── secret.key         # (Auto-created) Encryption key file
├── Exported.json      # (Generated on export)
├── README.md          # Documentation
└── .gitignore         # Git ignore rules
```

---

## 🧰 Requirements

* **Python 3.8 or higher**
* Install dependencies:

```
pip install cryptography
```

> 📝 Tkinter comes preinstalled with most Python distributions.

---

## ▶️ How to Run

1. **Clone the repository:**

   ```
   git clone https://github.com/<your-username>/password-manager.git
   cd password-manager
   ```

2. **Install dependencies:**

   ```
   pip install cryptography
   ```

3. **Run the application:**

   ```
   python main.py
   ```

4. The database (`passwords.db`) and encryption key (`secret.key`) will be automatically created on first run.

---

## 💾 Data Storage

All passwords are **encrypted using Fernet (AES-128 in CBC mode)** before being stored in `passwords.db`.
The encryption key is generated once and stored locally in `secret.key`.

> ⚠️ **Important:**
> If you delete the `secret.key` file, previously stored passwords **cannot be decrypted**.

---

## 🧠 Security Notes

* Passwords are encrypted at rest using a unique symmetric key.
* No internet or cloud storage — 100% offline.
* Designed for personal and local use.

---

## 📤 Exporting Passwords

Use the **"Export Passwords"** button in the app to generate `Exported.json`.

> This file contains **decrypted passwords** — handle it securely.

---

## 🧹 .gitignore Highlights

The `.gitignore` file excludes the following:

* `passwords.db`, `secret.key`, `Exported.json`
* Python cache files and virtual environments
* OS-specific files (`.DS_Store`, `Thumbs.db`)
* IDE configuration folders (`.vscode/`, `.idea/`)

---

## 📜 License

This project is open-source under the **MIT License**.

---

## 👨‍💻 Author

**Supratik Roy**
💡 Built for personal use and educational purposes.

---
