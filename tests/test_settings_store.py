from pm_core.settings_store import ensure_schema, bootstrap_first_run, unlock_vault

def test_bootstrap_and_unlock(tmp_path):
    db = tmp_path / "test.db"
    ensure_schema(str(db))
    crypto = bootstrap_first_run(str(db), "S3cure-Password!!", {"primary":"argon2id","argon2_memory_kib":32768,"argon2_time_cost":2,"argon2_parallelism":2,"salt_bytes":16})
    vc = unlock_vault(str(db), "S3cure-Password!!")
    assert vc.decrypt_text(crypto.encrypt_text("ok")) == "ok"
