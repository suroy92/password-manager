from pydantic import BaseModel
import os
from platformdirs import user_data_dir
from pathlib import Path

class Settings(BaseModel):
    env: str = os.getenv("PM_ENV", "dev")
    ui_serve: str = os.getenv("PM_UI_SERVE", "static")
    db_path: Path = Path(os.getenv("PM_DB_PATH", Path(user_data_dir('PasswordManager')) / "vault.db"))
    autolock_minutes: int = int(os.getenv("PM_AUTLOCK_MINUTES", "10"))
    clipboard_clear_seconds: int = int(os.getenv("PM_CLIPBOARD_CLEAR_SECONDS", "20"))

settings = Settings()
