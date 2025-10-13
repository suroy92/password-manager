# Integration Notes (Phase-1)

These modules are designed to be **drop-in** alongside your existing code.

## File map
- `pm_core/config.py` — defaults for security settings
- `pm_core/kdf.py` — Argon2id/scrypt derivation → Fernet key
- `pm_core/settings_store.py` — schema tables + first-run + unlock + change password
- `pm_core/vault_crypto.py` — wrapper around Fernet for text/json
- `pm_core/migration.py` — migrate from `secret.key` to master-password vault
- `pm_core/clipboard.py` — clipboard copy + auto-clear helper
- `pm_core/export_import.py` — encrypted export/import helpers
- `pm_core/logging_setup.py` — rotating logger with redaction
- `pm_core/ui/dialogs.py` — Tkinter dialogs for first-run/unlock/warnings
- `docs/SECURITY.md`, `docs/migrate_to_phase1.md`, `CHANGELOG.md`
- `.github/workflows/ci.yml` — CI with tests and dependency audit
- `requirements_phase1.txt` — new security dependencies
- `tests/` — minimal tests for critical paths

## Minimal code edits you need to make
1. **Replace `secret.key` flow** with master password bootstrap/unlock:
```python
# in your app startup (e.g., main.py)
from pm_core.settings_store import ensure_schema, unlock_vault, bootstrap_first_run
from pm_core.ui.dialogs import MasterPasswordDialog, UnlockDialog
from pm_core.config import DEFAULTS

DB_PATH = "passwords.db"

def get_master_password_first_run(root):
    dlg = MasterPasswordDialog(root)
    root.wait_window(dlg)
    return dlg.result

def get_master_password_unlock(root):
    dlg = UnlockDialog(root)
    root.wait_window(dlg)
    return dlg.result

def init_or_unlock(root):
    ensure_schema(DB_PATH)
    try:
        pw = get_master_password_unlock(root)
        return unlock_vault(DB_PATH, pw)
    except Exception:
        pw = get_master_password_first_run(root)
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
        return bootstrap_first_run(DB_PATH, pw, params)
```

2. **Clipboard usage** (when user clicks "Copy password"):
```python
from pm_core.clipboard import copy_to_clipboard

copy_to_clipboard(root, password_plaintext, timeout_seconds=20)
```

3. **Encrypted export/import buttons**:
```python
from pm_core.export_import import export_encrypted, import_encrypted

export_encrypted(DB_PATH, table="passwords", out_path="vault.pmjson.enc", master_password=master_password)
# To import:
import_encrypted(DB_PATH, in_path="vault.pmjson.enc", master_password=master_password, merge=False)
```

4. **Migration from `secret.key`** (one-time, optional):
```python
from pm_core.migration import migrate_from_secret_key
migrate_from_secret_key(DB_PATH, "secret.key", master_password, table_name="passwords", encrypted_fields=("password","recovery_codes"), id_column="id")
```

## Notes
- These helpers avoid touching your existing CRUD/UI code until you explicitly wire them.
- If your table/column names differ, adjust the parameters in the migration/export helpers.
- After wiring, **remove any code** that reads/writes `secret.key`.
