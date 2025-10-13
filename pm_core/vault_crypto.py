import json
from typing import Any, Dict
from cryptography.fernet import Fernet, InvalidToken

class VaultCrypto:
    def __init__(self, fernet_key: bytes):
        self._fernet = Fernet(fernet_key)

    def encrypt_text(self, plaintext: str) -> bytes:
        return self._fernet.encrypt(plaintext.encode('utf-8'))

    def decrypt_text(self, token: bytes) -> str:
        return self._fernet.decrypt(token).decode('utf-8')

    def encrypt_json(self, obj: Dict[str, Any]) -> bytes:
        return self._fernet.encrypt(json.dumps(obj, separators=(',', ':')).encode('utf-8'))

    def decrypt_json(self, token: bytes) -> Dict[str, Any]:
        data = self._fernet.decrypt(token)
        return json.loads(data.decode('utf-8'))

    @staticmethod
    def is_valid_token(fernet_key: bytes, token: bytes) -> bool:
        try:
            Fernet(fernet_key).decrypt(token)
            return True
        except InvalidToken:
            return False
