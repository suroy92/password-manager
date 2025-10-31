import secrets, string
from typing import List

AMBIGUOUS = set("Il1O0")
DEFAULT_SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/"

def _pool(chars: str, avoid_ambiguous: bool) -> List[str]:
    return [c for c in chars if not (avoid_ambiguous and c in AMBIGUOUS)]

def generate_password(
    length: int = 20,
    *,
    upper: bool = True,
    lower: bool = True,
    digits: bool = True,
    symbols: bool = True,
    avoid_ambiguous: bool = True,
) -> str:
    if length < 8 or length > 128:
        raise ValueError("length must be between 8 and 128")

    pools = []
    if upper:   pools.append(_pool(string.ascii_uppercase, avoid_ambiguous))
    if lower:   pools.append(_pool(string.ascii_lowercase, avoid_ambiguous))
    if digits:  pools.append(_pool(string.digits,         avoid_ambiguous))
    if symbols: pools.append(list(DEFAULT_SYMBOLS))
    if not pools: pools.append(_pool(string.ascii_letters + string.digits, avoid_ambiguous))

    pools = [p for p in pools if p] or [_pool(string.ascii_letters + string.digits, False)]

    password_chars = [secrets.choice(p) for p in pools]
    all_chars = [c for p in pools for c in p]
    while len(password_chars) < length:
        password_chars.append(secrets.choice(all_chars))
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars[:length])
