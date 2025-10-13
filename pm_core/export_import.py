import base64
import json
import os
import sqlite3
from typing import Optional, Dict, Any, List
from .settings_store import _connect, unlock_vault
from .kdf import derive_fernet_key
from .vault_crypto import VaultCrypto

def _read_all_rows(conn: sqlite3.Connection, table: str) -> List[Dict[str, Any]]:
    rows = conn.execute(f"SELECT * FROM {table}").fetchall()
    col_names = [d[1] for d in conn.execute(f"PRAGMA table_info({table})")]
    result = []
    for r in rows:
        obj = {}
        for name, val in zip(col_names, r):
            if isinstance(val, bytes):
                obj[name] = base64.b64encode(val).decode('ascii')
            else:
                obj[name] = val
        result.append(obj)
    return result

def export_encrypted(db_path: str, table: str, out_path: str, master_password: str, passphrase: Optional[str] = None) -> str:
    conn = _connect(db_path)
    try:
        data = _read_all_rows(conn, table)
    finally:
        conn.close()

    payload = json.dumps({"table": table, "records": data}).encode('utf-8')

    if passphrase:
        salt = os.urandom(16)
        kdf_params = {"primary": "argon2id", "argon2_memory_kib": 65536, "argon2_time_cost": 3, "argon2_parallelism": 2}
        key = derive_fernet_key(passphrase, salt, kdf_params)
        crypto = VaultCrypto(key)
        token = crypto.encrypt_json({"k": base64.b64encode(payload).decode('ascii')})
        out = {
            "version": 1,
            "using_vault_key": False,
            "kdf": kdf_params,
            "salt": base64.b64encode(salt).decode('ascii'),
            "ciphertext": base64.b64encode(token).decode('ascii'),
        }
    else:
        vc = unlock_vault(db_path, master_password)
        token = vc.encrypt_json({"k": base64.b64encode(payload).decode('ascii')})
        out = {
            "version": 1,
            "using_vault_key": True,
            "ciphertext": base64.b64encode(token).decode('ascii'),
        }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(',', ':'))

    return out_path

def import_encrypted(db_path: str, in_path: str, master_password: str, passphrase: Optional[str] = None, merge: bool = True) -> int:
    with open(in_path, "r", encoding="utf-8") as f:
        obj = json.load(f)

    using_vault_key = obj.get("using_vault_key", False)
    token_b = base64.b64decode(obj["ciphertext"])

    if using_vault_key:
        vc = unlock_vault(db_path, master_password)
        inner = vc.decrypt_json(token_b)
    else:
        if not passphrase:
            raise ValueError("Export requires passphrase to import")
        salt = base64.b64decode(obj["salt"])
        kdf_params = obj["kdf"]
        key = derive_fernet_key(passphrase, salt, kdf_params)
        crypto = VaultCrypto(key)
        inner = crypto.decrypt_json(token_b)

    payload = json.loads(base64.b64decode(inner["k"]).decode('utf-8'))
    table = payload["table"]
    records = payload["records"]

    conn = _connect(db_path)
    try:
        cols = [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]
        placeholders = ", ".join("?" for _ in cols)
        count = 0
        with conn:
            if not merge:
                conn.execute(f"DELETE FROM {table}")
            for rec in records:
                values = [base64.b64decode(rec[c]) if (c in rec and isinstance(rec[c], str) and rec[c].strip().endswith('=')) else rec.get(c) for c in cols]
                conn.execute(f"INSERT INTO {table} VALUES ({placeholders})", values)
                count += 1
        return count
    finally:
        conn.close()
