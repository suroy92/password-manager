from __future__ import annotations

import json
import secrets
from typing import Iterable

from .settings_store import _connect, ensure_schema, unlock_vault, get_setting, set_setting
from .kdf import derive_fernet_key
from .vault_crypto import VaultCrypto

def _to_bytes(x):
    if isinstance(x, bytes): return x
    if isinstance(x, memoryview): return bytes(x)
    if isinstance(x, str): return x.encode("utf-8")
    raise TypeError(type(x))

def rotate_master_password(
    db_path: str,
    old_password: str,
    new_password: str,
    table_name: str = "passwords",
    encrypted_fields: Iterable[str] = ("password",),
    id_column: str = "id",
) -> int:
    """
    Re-encrypt all selected columns with a NEW key derived from new_password.
    Also rotates the vault salt + canary. Returns number of rows processed.
    """
    ensure_schema(db_path)
    old_vc: VaultCrypto = unlock_vault(db_path, old_password)  # verifies old password

    conn = _connect(db_path)
    try:
        # Load KDF params and derive NEW key with NEW salt
        kdf_params_b = get_setting(conn, "kdf_params")
        if not kdf_params_b:
            raise RuntimeError("kdf_params missing; vault not initialized")
        kdf_params = json.loads(kdf_params_b.decode("utf-8"))
        new_salt = secrets.token_bytes(int(kdf_params.get("salt_bytes", 16)))
        new_key = derive_fernet_key(new_password, new_salt, kdf_params)
        new_vc = VaultCrypto(new_key)

        # Fetch rows to rewrap
        cols = list(encrypted_fields)
        col_expr = ", ".join(cols)
        rows = conn.execute(f"SELECT {id_column}, {col_expr} FROM {table_name}").fetchall()

        conn.execute("BEGIN")
        try:
            count = 0
            for row in rows:
                pk = row[0]
                old_vals = row[1:]
                new_vals = []
                for val in old_vals:
                    if val is None:
                        new_vals.append(None)
                        continue
                    plain = old_vc.decrypt_text(_to_bytes(val))
                    new_vals.append(new_vc.encrypt_text(plain))
                assigns = ", ".join(f"{c}=?" for c in cols)
                conn.execute(f"UPDATE {table_name} SET {assigns} WHERE {id_column}=?", (*new_vals, pk))
                count += 1

            # Switch vault salt + canary after data is safely rewrapped
            set_setting(conn, "salt", new_salt)
            set_setting(conn, "canary", new_vc.encrypt_text("canary-ok"))
            conn.execute("COMMIT")
            return count
        except Exception:
            conn.execute("ROLLBACK")
            raise
    finally:
        conn.close()
