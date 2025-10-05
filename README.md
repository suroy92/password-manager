# 🔐 Password Manager

A simple yet secure **Password Manager** built with **Python** and **Tkinter**, featuring encrypted password storage using the **Fernet** module from the `cryptography` library.
It allows you to **store, view, update, delete, and export** passwords in an easy-to-use desktop interface.

---

## 🚀 Features

* ✅ Store encrypted passwords securely in a local SQLite database
* ✅ Generate strong passwords with custom options
* ✅ View and update existing entries with instant decryption
* ✅ Delete entries safely (with confirmation dialog)
* ✅ Export all stored passwords to a JSON file
* ✅ Clean and responsive Tkinter interface
* ✅ Lightweight — no external dependencies beyond `cryptography`

---

## 🛠️ Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/<your-username>/Password-Manager.git
cd Password-Manager
```

### 2️⃣ Create and activate a virtual environment (optional but recommended)

```bash
# Create a virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

> 💡 Note: Tkinter comes pre-installed with most Python distributions.

---

## ▶️ Running the Application

Run the following command in your terminal:

```bash
python main.py
```

When launched, the application window will appear — you can begin adding and managing your passwords right away.

---

## 🧰 Usage Guide

### ➕ Add a New Password

* Click **“Store New”**
* Enter title, username, password, and recovery codes (optional)
* Click **Save**

### 🔍 View Details

* Select an entry and click **“View Details”**
* Password and details will be decrypted and shown

### ✏️ Update an Entry

* Select an entry and click **“Update”**
* Modify any field and save the updated information

### ❌ Delete an Entry

* Select an entry and click **“Delete”**
* A confirmation dialog ensures no accidental deletions

### 🔑 Generate a Password

* Click **“Generate Password”**
* Choose length, include numbers/symbols
* Copy and use it for your account

### 📤 Export Passwords

* Click **“Export Passwords”**
* A file named `Exported.json` will be created in your project folder

---

## 📂 Project Structure

```
Password-Manager/
├── main.py                # Main application file (Tkinter UI + core logic)
├── database.py            # Handles all SQLite database operations
├── encryption.py          # Encryption and decryption utilities (Fernet-based)
│
├── requirements.txt       # Python dependencies
├── .gitignore             # Files and folders to be ignored by Git
├── LICENSE                # MIT License file
├── README.md              # Project documentation (this file)
│
├── passwords.db           # SQLite database file (auto-created at runtime)
├── secret.key             # Encryption key file (auto-generated on first run)
└── Exported.json          # Optional export file containing saved passwords
```

---

## ⚙️ Technical Overview

* **Language:** Python 3.10+
* **GUI Framework:** Tkinter
* **Database:** SQLite
* **Encryption:** Fernet (AES, part of the `cryptography` library)
* **File Export:** JSON

---

## 🧑‍💻 Contributing

Contributions are welcome!
If you’d like to improve the UI, add new features, or refactor the architecture:

1. Fork this repository
2. Create a new branch (`feature/your-feature`)
3. Commit your changes
4. Push to your branch and open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License**.
See the [LICENSE](./LICENSE) file for more details.

---

## 💡 Acknowledgements

* [Python](https://www.python.org/)
* [Cryptography Library](https://cryptography.io/)
* [Tkinter GUI Toolkit](https://docs.python.org/3/library/tkinter.html)

---