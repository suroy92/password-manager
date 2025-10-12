#!/usr/bin/env python3
"""
Import plaintext Exported.json into the current DB, encrypting with the master key.

Usage:
  python import_plaintext_json.py --json Exported.json --db passwords.db --wipe
"""
import argparse, json, sqlite3, getpass
from pm_core.settings_store import ensure_schema, unlock_vault
from pm_core.vault_crypto import VaultCrypto

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="Exported.json")
    ap.add_argument("--db", default="passwords.db")
    ap.add_argument("--wipe", action="store_true", help="Delete all existing rows before import")
    args = ap.parse_args()

    ensure_schema(args.db)
    master = getpass.getpass("Enter master password: ")
    vc: VaultCrypto = unlock_vault(args.db, master)

    data = json.load(open(args.json, "r", encoding="utf-8"))
    conn = sqlite3.connect(args.db)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            username TEXT,
            password TEXT NOT NULL,
            recovery_codes TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()

    if args.wipe:
        cur.execute("DELETE FROM passwords")
        conn.commit()

    inserted = 0
    for rec in data:
        token = vc.encrypt_text(rec["password"])  # bytes (Fernet token)
        cur.execute(
            "INSERT INTO passwords (title, username, password, recovery_codes, created_at) VALUES (?,?,?,?,?)",
            (rec["title"], rec["username"], token, rec["recovery_codes"], rec["created_at"]),
        )
        inserted += 1
    conn.commit()
    conn.close()
    print(f"Imported {inserted} row(s) from {args.json} into {args.db} (encrypted).")

if __name__ == "__main__":
    main()
