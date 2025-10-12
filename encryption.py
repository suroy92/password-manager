"""
- First run: prompts user to set a master password and derives a Fernet key
  via Argon2id (scrypt fallback). Stores only KDF params + salt + a canary in DB.
- Subsequent runs: prompts to unlock and reconstructs the key in memory.
- Provides encrypt()/decrypt() helpers used by database.py.
- Keeps your existing generate_secure_password(length, include_numbers, include_symbols).
"""
from __future__ import annotations

from typing import Optional
import tkinter as tk
import secrets
import string

from pm_core.settings_store import ensure_schema, unlock_vault, bootstrap_first_run
from pm_core.vault_crypto import VaultCrypto
from pm_core.ui.dialogs import MasterPasswordDialog, UnlockDialog
from pm_core.config import DEFAULTS

DB_PATH = "passwords.db"
_CRYPTO: Optional[VaultCrypto] = None

def _first_run_pw(root: tk.Tk) -> str:
    dlg = MasterPasswordDialog(root)
    root.wait_window(dlg)
    if not dlg.result:
        raise SystemExit("Master password setup cancelled.")
    return dlg.result

def _unlock_pw(root: tk.Tk) -> str:
    dlg = UnlockDialog(root)
    root.wait_window(dlg)
    if not dlg.result:
        raise SystemExit("Unlock cancelled.")
    return dlg.result

def initialize_vault(root: tk.Tk) -> VaultCrypto:
    """
    Call once, after creating the Tk root, before you touch encrypt()/decrypt().
    """
    global _CRYPTO
    ensure_schema(DB_PATH)
    try:
        # Try to unlock existing vault
        pw = _unlock_pw(root)
        _CRYPTO = unlock_vault(DB_PATH, pw)
    except Exception:
        # First run bootstrap
        pw = _first_run_pw(root)
        params = {
            "primary": "argon2id",
            "argon2_memory_kib": DEFAULTS.kdf.argon2_memory_kib,
            "argon2_time_cost": DEFAULTS.kdf.argon2_time_cost,
            "argon2_parallelism": DEFAULTS.kdf.argon2_parallelism,
            "salt_bytes": DEFAULTS.kdf.salt_bytes,
            "scrypt_N": DEFAULTS.kdf.scrypt_N,
            "scrypt_r": DEFAULTS.kdf.scrypt_r,
            "scrypt_p": DEFAULTS.kdf.scrypt_p,
        }
        _CRYPTO = bootstrap_first_run(DB_PATH, pw, params)
    return _CRYPTO

def _to_bytes(token) -> bytes:
    if isinstance(token, bytes):
        return token
    if isinstance(token, memoryview):
        return bytes(token)
    if isinstance(token, str):
        return token.encode("utf-8")
    raise TypeError(f"Unsupported token type for decrypt(): {type(token)!r}")

def encrypt(plaintext: str) -> bytes:
    """Encrypt a plaintext string into a Fernet token (bytes) for SQLite storage."""
    if _CRYPTO is None:
        raise RuntimeError("Vault not initialized. Call initialize_vault(root) first.")
    return _CRYPTO.encrypt_text(plaintext)

def decrypt(token) -> str:
    """Decrypt a Fernet token (bytes/str/memoryview) back to plaintext string."""
    if _CRYPTO is None:
        raise RuntimeError("Vault not initialized. Call initialize_vault(root) first.")
    return _CRYPTO.decrypt_text(_to_bytes(token))

# ---- Password generator (keeps your old API name/signature) ----
def generate_secure_password(length: int = 12, include_numbers: bool = True, include_symbols: bool = True) -> str:
    """
    Generate a random password with optional numbers/symbols.
    Ensures at least one of each selected class is present when possible.
    """
    if length < 4:
        length = 4  # sane floor

    letters = string.ascii_letters
    digits = string.digits if include_numbers else ""
    symbols = string.punctuation if include_symbols else ""

    pool = letters + digits + symbols or letters

    # Guarantee inclusion for selected classes
    required = []
    if include_numbers:
        required.append(secrets.choice(string.digits))
    if include_symbols:
        required.append(secrets.choice(string.punctuation))
    required.append(secrets.choice(string.ascii_lowercase))
    required.append(secrets.choice(string.ascii_uppercase))

    # Fill the rest
    remaining = max(0, length - len(required))
    body = [secrets.choice(pool) for _ in range(remaining)]
    chars = required + body

    # Shuffle using secrets (not random)
    for i in range(len(chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        chars[i], chars[j] = chars[j], chars[i]

    return "".join(chars[:length])
