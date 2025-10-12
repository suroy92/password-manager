# Changelog

## [1.0.0-phase1] - 2025-10-12
### Added
- Master password with Argon2id KDF (scrypt fallback), per-vault salt, and canary.
- Auto-lock scaffolding (idle timer utilities, to be wired into UI).
- Clipboard auto-clear helper.
- Encrypted export/import (`vault.pmjson.enc`) plus plaintext export guard dialog.
- Centralized logging with redaction and rotating handler.
- Schema versioning tables `settings` and `schema_migrations`.
- Migration helper from `secret.key` to master password flow.
- Basic unit tests for KDF, settings store, and export/import.

### Security
- No secrets in logs; crash info sanitized (recommend wiring a top-level handler).
