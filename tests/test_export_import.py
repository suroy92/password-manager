import sqlite3
from pm_core.settings_store import ensure_schema, bootstrap_first_run
from pm_core.export_import import export_encrypted, import_encrypted

def test_export_import_roundtrip(tmp_path):
    db = tmp_path / "vault.db"
    ensure_schema(str(db))
    bootstrap_first_run(str(db), "P@ssw0rd-123", {"primary":"argon2id","argon2_memory_kib":32768,"argon2_time_cost":2,"argon2_parallelism":2,"salt_bytes":16})

    conn = sqlite3.connect(str(db))
    with conn:
        conn.execute("CREATE TABLE passwords (id INTEGER PRIMARY KEY, title TEXT, username TEXT, password BLOB, recovery_codes BLOB)")
        conn.execute("INSERT INTO passwords(title, username, password, recovery_codes) VALUES (?,?,?,?)", ("t", "u", b"c2VjcmV0", b"bm9uZQ=="))
    conn.close()

    out = tmp_path / "vault.pmjson.enc"
    export_encrypted(str(db), "passwords", str(out), "P@ssw0rd-123")
    assert out.exists()

    db2 = tmp_path / "vault2.db"
    ensure_schema(str(db2))
    bootstrap_first_run(str(db2), "P@ssw0rd-123", {"primary":"argon2id","argon2_memory_kib":32768,"argon2_time_cost":2,"argon2_parallelism":2,"salt_bytes":16})
    count = import_encrypted(str(db2), str(out), "P@ssw0rd-123", merge=False)
    assert count == 1
