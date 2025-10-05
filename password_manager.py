import sqlite3
import json
import os
import random
import string
from cryptography.fernet import Fernet
from datetime import datetime

# --- Configuration and Database Setup ---
DB_FILE = 'passwords.db'
KEY_FILE = 'secret.key'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    return conn

def create_tables():
    """Creates the passwords table if it doesn't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
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

def generate_key():
    """Generates a new Fernet key if one doesn't exist and returns it."""
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as key_file:
            key_file.write(key)
    with open(KEY_FILE, 'rb') as key_file:
        return key_file.read()

KEY = generate_key()
f = Fernet(KEY)

# --- Password Generation ---
def generate_secure_password(length=10, numbers=False, symbols=False):
    """
    Generates a random, secure password.

    Args:
        length (int): The length of the password.
        numbers (bool): True to include numbers, False otherwise.
        symbols (bool): True to include symbols, False otherwise.
    
    Returns:
        str: The generated password.
    """
    chars = string.ascii_letters
    if numbers:
        chars += string.digits
    if symbols:
        chars += string.punctuation
    
    if length < 10:
        length = 10 # Minimum password length
        
    return ''.join(random.choice(chars) for _ in range(length))

# --- CRUD Operations ---
def store_password(title, username, password, recovery_codes=None):
    """Stores a new password entry in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    encrypted_password = f.encrypt(password.encode()).decode()
    
    cursor.execute("""
        INSERT INTO passwords (title, username, password, recovery_codes, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (title, username, encrypted_password, recovery_codes, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    return True

def list_passwords():
    """Retrieves a list of all password titles and usernames."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, username FROM passwords")
    passwords = cursor.fetchall()
    conn.close()
    return passwords

def get_password_details(id):
    """Retrieves a single password entry and decrypts the password."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM passwords WHERE id = ?", (id,))
    details = cursor.fetchone()
    conn.close()
    
    if details:
        decrypted_password = f.decrypt(details[3].encode()).decode()
        return {
            "id": details[0],
            "title": details[1],
            "username": details[2],
            "password": decrypted_password,
            "recovery_codes": details[4],
            "created_at": details[5]
        }
    return None

def update_password(id, new_title, new_username, new_password, new_recovery_codes=None):
    """Updates an existing password entry in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    encrypted_password = f.encrypt(new_password.encode()).decode()
    
    cursor.execute("""
        UPDATE passwords 
        SET title = ?, username = ?, password = ?, recovery_codes = ?
        WHERE id = ?
    """, (new_title, new_username, encrypted_password, new_recovery_codes, id))
    
    conn.commit()
    conn.close()
    return True

def migrate_up(data):
    """Migrates passwords from a JSON file into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("BEGIN TRANSACTION")
    try:
        for item in data:
            encrypted_password = f.encrypt(item['password'].encode()).decode()
            cursor.execute("""
                INSERT INTO passwords (title, username, password, recovery_codes, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (item['title'], item['username'], encrypted_password, item['recovery_codes'], datetime.now().isoformat()))
        conn.commit()
        return "Migration successful!"
    except Exception as e:
        conn.rollback()
        return f"Migration failed: {e}"
    finally:
        conn.close()

def migrate_down():
    """Deletes all passwords from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM passwords")
    conn.commit()
    conn.close()
    return "All passwords cleared from DB."

def export_passwords():
    """Exports all passwords to a JSON file."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM passwords")
    records = cursor.fetchall()
    conn.close()
    
    exported_data = []
    for record in records:
        decrypted_password = f.decrypt(record[3].encode()).decode()
        exported_data.append({
            "id": record[0],
            "title": record[1],
            "username": record[2],
            "password": decrypted_password,
            "recovery_codes": record[4],
            "created_at": record[5]
        })
    
    with open("Exported.json", "w") as json_file:
        json.dump(exported_data, json_file, indent=4)
        
    return f"Passwords exported to {os.getcwd()}/Exported.json"

# --- Color Class for Improved Readability ---
class Color:
    """ANSI escape codes for console text colors."""
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# --- Main CLI Logic ---
def main():
    """Main function to run the command-line interface."""
    create_tables()

    while True:
        print(f"\n{Color.CYAN}--- Password Manager Menu ---{Color.END}")
        print(f"{Color.CYAN}1. Generate a new password{Color.END}")
        print(f"{Color.CYAN}2. Store a new password{Color.END}")
        print(f"{Color.CYAN}3. List all passwords{Color.END}")
        print(f"{Color.CYAN}4. Show details of a specific password{Color.END}")
        print(f"{Color.CYAN}5. Update an existing password{Color.END}")
        print(f"{Color.CYAN}6. Migrate passwords from a file{Color.END}")
        print(f"{Color.CYAN}7. Clear all passwords{Color.END}")
        print(f"{Color.CYAN}8. Export all passwords to a file{Color.END}")
        print(f"{Color.CYAN}9. Exit{Color.END}")
        print(f"{Color.CYAN}----------------------------{Color.END}")

        choice = input(f"{Color.BLUE}Enter your choice (1-9): {Color.END}")

        if choice == '1':
            print(f"\n{Color.YELLOW}Generating a secure password...{Color.END}")
            length_input = input(f"{Color.GREEN}Enter password length (min 10): {Color.END}") or "10"
            length = max(10, int(length_input))
            
            include_numbers = input(f"{Color.GREEN}Include numbers? (y/n): {Color.END}").lower() == 'y'
            include_symbols = input(f"{Color.GREEN}Include symbols? (y/n): {Color.END}").lower() == 'y'
            
            password = generate_secure_password(length, include_numbers, include_symbols)
            print(f"{Color.YELLOW}Generated Password:{Color.END} {Color.BOLD}{password}{Color.END}")
            
            save_option = input(f"{Color.GREEN}Do you want to save this password? (y/n): {Color.END}").lower()
            if save_option == 'y':
                title = input(f"{Color.GREEN}Enter title: {Color.END}")
                username = input(f"{Color.GREEN}Enter username: {Color.END}")
                recovery_codes = input(f"{Color.GREEN}Enter recovery codes (comma-separated): {Color.END}")
                store_password(title, username, password, recovery_codes)
                print(f"{Color.GREEN}Password stored successfully!{Color.END}")
        
        elif choice == '2':
            print(f"\n{Color.YELLOW}Storing a new password...{Color.END}")
            title = input(f"{Color.GREEN}Enter title: {Color.END}")
            username = input(f"{Color.GREEN}Enter username: {Color.END}")
            password = input(f"{Color.GREEN}Enter password: {Color.END}")
            recovery_codes = input(f"{Color.GREEN}Enter recovery codes (comma-separated): {Color.END}")
            store_password(title, username, password, recovery_codes)
            print(f"{Color.GREEN}Password stored successfully!{Color.END}")

        elif choice == '3':
            print(f"\n{Color.YELLOW}Listing all passwords...{Color.END}")
            passwords = list_passwords()
            if passwords:
                print(f"{Color.BOLD}{Color.UNDERLINE}{Color.CYAN}{'ID':<5} {'Title':<50} {'Username':<50}{Color.END}")
                print("-" * 105)
                for pwd in passwords:
                    print(f"{Color.YELLOW}{pwd[0]:<5}{Color.END} {pwd[1]:<50} {pwd[2]:<50}")
            else:
                print(f"{Color.RED}No passwords found.{Color.END}")
        
        elif choice == '4':
            print(f"\n{Color.YELLOW}Showing password details...{Color.END}")
            try:
                password_id = int(input(f"{Color.GREEN}Enter password ID: {Color.END}"))
                details = get_password_details(password_id)
                if details:
                    print(f"\n{Color.YELLOW}Password Details:{Color.END}")
                    print("-" * 30)
                    for key, value in details.items():
                        print(f"{Color.DARKCYAN}{key:<20}: {Color.END}{value}")
                else:
                    print(f"{Color.RED}No password found with ID {password_id}{Color.END}")
            except ValueError:
                print(f"{Color.RED}Invalid input. Please enter a number.{Color.END}")
        
        elif choice == '5':
            print(f"\n{Color.YELLOW}Updating an existing password...{Color.END}")
            try:
                password_id = int(input(f"{Color.GREEN}Enter the ID of the password to update: {Color.END}"))
                details = get_password_details(password_id)
                if not details:
                    print(f"{Color.RED}No password found with ID {password_id}{Color.END}")
                    continue

                print(f"{Color.BLUE}Current details for ID {password_id}:{Color.END}")
                print(f"Title: {details['title']}")
                print(f"Username: {details['username']}")
                print("Password: [Hidden]")

                new_title = input(f"{Color.GREEN}Enter new title (or press Enter to keep '{details['title']}'): {Color.END}") or details['title']
                new_username = input(f"{Color.GREEN}Enter new username (or press Enter to keep '{details['username']}'): {Color.END}") or details['username']
                new_password = input(f"{Color.GREEN}Enter new password (or press Enter to keep current): {Color.END}")
                new_password = new_password or details['password']
                new_recovery_codes = input(f"{Color.GREEN}Enter new recovery codes (or press Enter to keep '{details['recovery_codes']}'): {Color.END}") or details['recovery_codes']

                if update_password(password_id, new_title, new_username, new_password, new_recovery_codes):
                    print(f"{Color.GREEN}Password updated successfully! ✅{Color.END}")
                else:
                    print(f"{Color.RED}Failed to update password. 😔{Color.END}")

            except ValueError:
                print(f"{Color.RED}Invalid input. Please enter a valid password ID.{Color.END}")
        
        elif choice == '6':
            print(f"\n{Color.YELLOW}Starting migration...{Color.END}")
            if not os.path.exists("Exported.json"):
                print(f"{Color.RED}Error: Exported.json file not found.{Color.END}")
                continue
            with open("Exported.json", 'r') as f:
                records = json.load(f)
            response = migrate_up(records)
            print(response)

        elif choice == '7':
            response = migrate_down()
            print(f"{Color.GREEN}{response}{Color.END}")

        elif choice == '8':
            response = export_passwords()
            print(f"{Color.GREEN}{response}{Color.END}")

        elif choice == '9':
            print(f"{Color.GREEN}Exiting. Goodbye! 👋{Color.END}")
            break

        else:
            print(f"{Color.RED}Invalid choice. Please enter a number from 1 to 9.{Color.END}")


if __name__ == "__main__":
    main()