# Changelog

## [1.1.0-ui] - 2025-10-12
### Added
- Modernized desktop UI with ttkbootstrap (no runtime theme toggle).
- Classic **Menubar**:
  - **File** → Store New, Generate Password, Export (Plaintext), Export (Encrypted), Exit
  - **Security** → Change Master Password…
- **Search bar** above the table with live filtering by title/username.
- **Sortable** table headers (click to sort).
- **Manual row striping**, larger row height for readability.
- **Show/Hide** password toggle in dialogs.
- **Password strength meter** in create/update dialogs.
- **Context menu** on entries (right-click: View, Copy, Update, Delete).
- **Non-blocking toasts** and a **status bar** for feedback.
- **Global font** application with platform-aware fallbacks  
  (Windows prefers **Inter**, then Segoe UI Variable/Segoe UI).

### Changed
- Replaced top action buttons with classic menubar.
- Default visual style refreshed via ttkbootstrap.
- Minor UX copy and layout polish.

### Dependencies
- Add `ttkbootstrap` to `requirements.txt`.

### Notes
- Security model unchanged from 1.0.0-phase1; plaintext export still available but discouraged in favor of encrypted export.

---

## [1.0.0-phase1] - 2025-10-12
### Added
- Master password with Argon2id KDF (scrypt fallback), per-vault salt, and canary.
- Auto-lock scaffolding (idle timer utilities).
- Clipboard auto-clear helper.
- Encrypted export/import (`vault.pmjson.enc`) plus plaintext export guard dialog.
- Centralized logging with redaction and rotating handler.
- Schema versioning tables `settings` and `schema_migrations`.
- Migration helper from `secret.key` to master password flow.
- Basic unit tests for KDF, settings store, and export/import.

### Security
- No secrets in logs; crash info sanitized.
