# Backend increment 02 — recovery codes + password generator

Install and run:

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e .
python run_api.py
```

Endpoints added:
- POST /api/password/generate { length, upper, lower, digits, symbols, avoid_ambiguous }
- entries now include `recovery_codes` (array of strings). Use `?reveal=true` on GET/POST/PUT to include sensitive fields in response.
