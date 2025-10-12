import base64
import logging
import os
import sqlite3
from typing import Sequence

from cryptography.fernet import Fernet, InvalidToken

from .settings_store import _connect, unlock_vault
from .vault_crypto import VaultCrypto

def _read_secret_key(secret_key_path: str) -> bytes:
    with open(secret_key_path, 'rb') as f:
        raw = f.read().strip()
    try:
        if len(raw) == 32:
            return base64.urlsafe_b64encode(raw)
        Fernet(raw)  # validate
        return raw
    except Exception as e:
        raise ValueError("secret.key is not a valid Fernet key") from e

def migrate_from_secret_key(
    db_path: str,
    secret_key_path: str,
    master_password: str,
    table_name: str = "passwords",
    encrypted_fields: Sequence[str] = ("password", "recovery_codes"),
    id_column: str = "id",
) -> int:
    if not os.path.exists(secret_key_path):
        raise FileNotFoundError(secret_key_path)

    old_key = _read_secret_key(secret_key_path)
    old_fernet = Fernet(old_key)
    new_crypto: VaultCrypto = unlock_vault(db_path, master_password)

    conn = _connect(db_path)
    count = 0
    try:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cur.fetchone():
            raise RuntimeError(f"Table '{table_name}' not found.")

        pragma = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        cols = {row[1] for row in pragma}
        to_process = [c for c in encrypted_fields if c in cols]
        if not to_process:
            raise RuntimeError(f"No matching encrypted fields found in {table_name}.")

        with conn:
            rows = conn.execute(f"SELECT {id_column}, {', '.join(to_process)} FROM {table_name}").fetchall()
            for row in rows:
                _id = row[0]
                old_values = row[1:]
                new_values = []
                for val in old_values:
                    if val is None:
                        new_values.append(None)
                        continue
                    try:
                        decrypted = old_fernet.decrypt(val).decode('utf-8')
                    except InvalidToken:
                        try:
                            decrypted = val.decode('utf-8')
                        except Exception:
                            decrypted = str(val)
                    new_values.append(new_crypto.encrypt_text(decrypted))
                assignments = ", ".join(f"{col} = ?" for col in to_process)
                conn.execute(
                    f"UPDATE {table_name} SET {assignments} WHERE {id_column} = ?",
                    (*new_values, _id),
                )
                count += 1
    finally:
        conn.close()

    try:
        size = os.path.getsize(secret_key_path)
        with open(secret_key_path, 'r+b') as f:
            f.write(os.urandom(size))
            f.flush()
            os.fsync(f.fileno())
        os.remove(secret_key_path)
    except Exception:
        logging.warning("Could not securely delete secret.key; please remove it manually.")

    return count
