# Migration Guide: Phase-1 Hardening

This guide shows how to move from `secret.key` to a master-password-protected vault.

## 1) Initialize or Unlock
- On first launch after upgrade, the app should prompt for a **master password** (first run) or **unlock** (if already initialized).

## 2) Run Migration
Programmatically, call:
```python
from pm_core.settings_store import ensure_schema, bootstrap_first_run, unlock_vault
from pm_core.migration import migrate_from_secret_key

DB = "passwords.db"   # adjust if needed
SECRET = "secret.key" # legacy key file
# If this is first initialization:
#   bootstrap_first_run(DB, master_password, kdf_params_dict)
# Else, just unlock:
#   unlock_vault(DB, master_password)

updated = migrate_from_secret_key(DB, SECRET, master_password, table_name="passwords", encrypted_fields=("password","recovery_codes"), id_column="id")
print("Migrated rows:", updated)
```

## 3) Verify & Cleanup
- Confirm that unlock works with the master password.
- The migration will attempt a best-effort secure deletion of `secret.key` (not guaranteed on SSDs). Remove the file manually if it still exists.

## 4) Rollback
- Restore your pre-migration database backup if needed.
