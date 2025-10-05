import os
from cryptography.fernet import Fernet
import random, string

KEY_FILE = "secret.key"

def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    with open(KEY_FILE, "rb") as f:
        return f.read()

KEY = generate_key()
f = Fernet(KEY)

def encrypt(plain_text):
    return f.encrypt(plain_text.encode()).decode()

def decrypt(cipher_text):
    return f.decrypt(cipher_text.encode()).decode()

def generate_secure_password(length=10, numbers=False, symbols=False):
    chars = string.ascii_letters
    if numbers:
        chars += string.digits
    if symbols:
        chars += string.punctuation
    if length < 10:
        length = 10
    return ''.join(random.choice(chars) for _ in range(length))
