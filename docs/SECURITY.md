# Security Policy (Phase 1)

## Threat Model (high-level)
- Protect secrets at rest on the local machine against casual access (file theft, basic malware).
- Defend against shoulder-surfing and unattended sessions (auto-lock).
- Prevent accidental plaintext leaks (encrypted export by default).
- **Out of scope** (Phase 1): kernel-level attackers, advanced keyloggers, physical cold-boot attacks.

## Master Password
- The master password is **unrecoverable**. If you forget it, your vault cannot be decrypted.
- A canary value is used to verify correct unlock without revealing secrets.

## Key Derivation
- Primary: **Argon2id** with memory/time/cpu hardening; fallback to **scrypt** when Argon2 isn’t available.
- Per-vault random salt is stored with KDF parameters.

## Exports
- Encrypted export is the default; plaintext export requires multi-step confirmation.
- Import validates integrity and rejects tampered files.

## Responsible Disclosure
Please open a private report via email (replace with your address) rather than a public issue for potential vulnerabilities.
