import base64
from typing import Dict
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

try:
    # argon2-cffi low-level API for deterministic KDF
    from argon2.low_level import Type, hash_secret_raw
    has_argon2 = True
except Exception:  # optional
    has_argon2 = False

def _b(s: str) -> bytes:
    return s.encode('utf-8') if isinstance(s, str) else s

def derive_key_argon2id(password: str, salt: bytes, params: Dict) -> bytes:
    if not has_argon2:
        raise RuntimeError("argon2-cffi not available")
    mem = int(params.get("argon2_memory_kib", 65536))
    time_cost = int(params.get("argon2_time_cost", 3))
    parallelism = int(params.get("argon2_parallelism", 2))
    raw = hash_secret_raw(
        secret=_b(password),
        salt=salt,
        time_cost=time_cost,
        memory_cost=mem,
        parallelism=parallelism,
        hash_len=32,
        type=Type.ID,
    )
    return raw  # 32 bytes

def derive_key_scrypt(password: str, salt: bytes, params: Dict) -> bytes:
    N = int(params.get("scrypt_N", 2**14))
    r = int(params.get("scrypt_r", 8))
    p = int(params.get("scrypt_p", 1))
    kdf = Scrypt(salt=salt, length=32, n=N, r=r, p=p)
    return kdf.derive(_b(password))

def derive_fernet_key(password: str, salt: bytes, params: Dict) -> bytes:
    # Derive raw 32 bytes then base64-url encode to Fernet key format
    algo = params.get("primary", "argon2id")
    try:
        if algo == "argon2id":
            raw = derive_key_argon2id(password, salt, params)
        else:
            raw = derive_key_scrypt(password, salt, params)
    except Exception:
        # Fallback to scrypt if argon2 isn't available at runtime
        raw = derive_key_scrypt(password, salt, params)
    return base64.urlsafe_b64encode(raw)  # 44 bytes suitable for Fernet
