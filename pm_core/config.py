from dataclasses import dataclass

@dataclass(frozen=True)
class PasswordPolicy:
    min_length: int = 12
    require_classes: int = 3  # of [upper, lower, digit, symbol]
    block_common: bool = True

@dataclass(frozen=True)
class SessionLock:
    idle_minutes: int = 5
    on_minimize: bool = True
    on_sleep: bool = True  # best-effort

@dataclass(frozen=True)
class ClipboardCfg:
    auto_clear_seconds: int = 20
    allow_copy: bool = True

@dataclass(frozen=True)
class ExportCfg:
    encrypted_default: bool = True
    allow_plaintext_with_confirmation: bool = True

@dataclass(frozen=True)
class LoggingCfg:
    level: str = "INFO"
    rotate_mb: int = 5
    keep_files: int = 5

@dataclass(frozen=True)
class CrashReportCfg:
    include_env_opt_in: bool = False

@dataclass(frozen=True)
class KdfParams:
    primary: str = "argon2id"
    argon2_memory_kib: int = 65536
    argon2_time_cost: int = 3
    argon2_parallelism: int = 2
    fallback: str = "scrypt"
    scrypt_N: int = 16384
    scrypt_r: int = 8
    scrypt_p: int = 1
    salt_bytes: int = 16

@dataclass(frozen=True)
class Defaults:
    password_policy: PasswordPolicy = PasswordPolicy()
    session_lock: SessionLock = SessionLock()
    clipboard: ClipboardCfg = ClipboardCfg()
    export: ExportCfg = ExportCfg()
    logging: LoggingCfg = LoggingCfg()
    crash_report: CrashReportCfg = CrashReportCfg()
    kdf: KdfParams = KdfParams()

DEFAULTS = Defaults()
