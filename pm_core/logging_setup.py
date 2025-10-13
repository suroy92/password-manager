import logging
import os
from logging.handlers import RotatingFileHandler

SENSITIVE_KEYS = {"password", "secret", "token", "key", "recovery", "passphrase"}

def _redact(msg: str) -> str:
    lower = msg.lower()
    for k in SENSITIVE_KEYS:
        if k in lower:
            msg = msg.replace(k, f"{k[0]}***{k[-1]}")
    return msg

class RedactingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        record.msg = _redact(str(record.msg))
        return super().format(record)

def setup_logger(level: str = "INFO", rotate_mb: int = 5, keep_files: int = 5) -> logging.Logger:
    logger = logging.getLogger("pm")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    os.makedirs("logs", exist_ok=True)
    handler = RotatingFileHandler("logs/app.log", maxBytes=rotate_mb * 1024 * 1024, backupCount=keep_files)
    formatter = RedactingFormatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    logger.addHandler(stream)

    return logger
