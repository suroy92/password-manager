import json
import os
import sqlite3
import secrets
from typing import Optional, Dict

from .kdf import derive_fernet_key
from .vault_crypto import VaultCrypto

SETTINGS_TABLE_SQL = """CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value BLOB NOT NULL
);
"""

MIGRATIONS_TABLE_SQL = """CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY
);
"""

def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, isolation_level=None, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def ensure_schema(db_path: str) -> None:
    conn = _connect(db_path)
    with conn:
        conn.execute(SETTINGS_TABLE_SQL)
        conn.execute(MIGRATIONS_TABLE_SQL)
        cur = conn.execute("SELECT COUNT(*) FROM schema_migrations")
        if cur.fetchone()[0] == 0:
            conn.execute("INSERT INTO schema_migrations(version) VALUES (1)")
    conn.close()

def get_setting(conn: sqlite3.Connection, key: str) -> Optional[bytes]:
    cur = conn.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = cur.fetchone()
    return row[0] if row else None

def set_setting(conn: sqlite3.Connection, key: str, value: bytes) -> None:
    conn.execute("INSERT OR REPLACE INTO settings(key, value) VALUES (?, ?)", (key, value))

def bootstrap_first_run(db_path: str, master_password: str, kdf_params: Dict) -> VaultCrypto:
    ensure_schema(db_path)
    conn = _connect(db_path)
    with conn:
        if get_setting(conn, "kdf_params"):
            raise RuntimeError("Vault already initialized")
        salt = secrets.token_bytes(int(kdf_params.get("salt_bytes", 16)))
        fernet_key = derive_fernet_key(master_password, salt, kdf_params)
        set_setting(conn, "salt", salt)
        set_setting(conn, "kdf_params", json.dumps(kdf_params).encode("utf-8"))
        crypto = VaultCrypto(fernet_key)
        canary = crypto.encrypt_text("canary-ok")
        set_setting(conn, "canary", canary)
    conn.close()
    return crypto

def unlock_vault(db_path: str, master_password: str) -> VaultCrypto:
    conn = _connect(db_path)
    try:
        salt = get_setting(conn, "salt")
        kdf_params_b = get_setting(conn, "kdf_params")
        canary = get_setting(conn, "canary")
        if not (salt and kdf_params_b and canary):
            raise RuntimeError("Vault not initialized")
        kdf_params = json.loads(kdf_params_b.decode("utf-8"))
        fernet_key = derive_fernet_key(master_password, salt, kdf_params)
        crypto = VaultCrypto(fernet_key)
        txt = crypto.decrypt_text(canary)
        if txt != "canary-ok":
            raise PermissionError("Invalid master password")
        return crypto
    finally:
        conn.close()

def change_master_password(db_path: str, old_password: str, new_password: str) -> None:
    conn = _connect(db_path)
    try:
        salt = get_setting(conn, "salt")
        kdf_params_b = get_setting(conn, "kdf_params")
        canary = get_setting(conn, "canary")
        if not (salt and kdf_params_b and canary):
            raise RuntimeError("Vault not initialized")
        kdf_params = json.loads(kdf_params_b.decode("utf-8"))
        old_key = derive_fernet_key(old_password, salt, kdf_params)
        old_crypto = VaultCrypto(old_key)
        if old_crypto.decrypt_text(canary) != "canary-ok":
            raise PermissionError("Invalid current master password")

        new_salt = os.urandom(int(kdf_params.get("salt_bytes", 16)))
        new_key = derive_fernet_key(new_password, new_salt, kdf_params)
        new_crypto = VaultCrypto(new_key)
        with conn:
            set_setting(conn, "salt", new_salt)
            set_setting(conn, "canary", new_crypto.encrypt_text("canary-ok"))
    finally:
        conn.close()
