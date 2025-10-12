import sqlite3
from datetime import datetime
# Phase-1: only import encrypt/decrypt (no global Fernet instance)
from encryption import encrypt, decrypt

DB_FILE = "passwords.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Note: column type left as TEXT for compatibility with existing DBs.
    # SQLite will happily store the Fernet token bytes in a TEXT-typed column,
    # but if you're creating a fresh DB you can switch 'password TEXT' -> 'password BLOB'.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            username TEXT,
            password TEXT NOT NULL,
            recovery_codes TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def store_password(title, username, password, recovery_codes=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    token = encrypt(password)  # bytes (Fernet token)
    cursor.execute("""
        INSERT INTO passwords (title, username, password, recovery_codes, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (title, username, token, recovery_codes, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return True

def list_passwords():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, username FROM passwords")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_password_details(entry_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM passwords WHERE id = ?", (entry_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        # row[3] may be bytes, memoryview, or str depending on SQLite/python build.
        password_plain = decrypt(row[3])
        return {
            "id": row[0],
            "title": row[1],
            "username": row[2],
            "password": password_plain,
            "recovery_codes": row[4],
            "created_at": row[5]
        }
    return None

def update_password(entry_id, title, username, password, recovery_codes=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    token = encrypt(password)  # bytes
    cursor.execute("""
        UPDATE passwords
        SET title = ?, username = ?, password = ?, recovery_codes = ?
        WHERE id = ?
    """, (title, username, token, recovery_codes, entry_id))
    conn.commit()
    conn.close()
    return True

def delete_password_entry(entry_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM passwords WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    return True

def export_passwords():
    import json
    import os
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM passwords")
    records = cursor.fetchall()
    conn.close()

    exported_data = []
    for record in records:
        exported_data.append({
            "id": record[0],
            "title": record[1],
            "username": record[2],
            "password": decrypt(record[3]),
            "recovery_codes": record[4],
            "created_at": record[5]
        })

    file_path = os.path.join(os.getcwd(), "Exported.json")
    with open(file_path, "w", encoding="utf-8") as f_json:
        json.dump(exported_data, f_json, indent=4)

    return f"Passwords exported to {file_path}"
