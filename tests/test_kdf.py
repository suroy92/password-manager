from pm_core.kdf import derive_fernet_key

def test_kdf_deterministic():
    salt = b"\x00" * 16
    params = {"primary": "argon2id", "argon2_memory_kib": 65536, "argon2_time_cost": 2, "argon2_parallelism": 2}
    k1 = derive_fernet_key("passw0rd!", salt, params)
    k2 = derive_fernet_key("passw0rd!", salt, params)
    assert k1 == k2 and len(k1) >= 32
