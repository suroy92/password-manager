from __future__ import annotations
from argon2.low_level import Type, hash_secret_raw
from os import urandom

MEMORY_KIB = 64 * 1024
TIME_COST = 3
PARALLELISM = 1
DK_LEN = 32

def gen_salt(n: int = 16) -> bytes:
    return urandom(n)

def derive_key(password: str, salt: bytes) -> bytes:
    return hash_secret_raw(
        secret=password.encode("utf-8"),
        salt=salt,
        time_cost=TIME_COST,
        memory_cost=MEMORY_KIB,
        parallelism=PARALLELISM,
        hash_len=DK_LEN,
        type=Type.ID,
    )
