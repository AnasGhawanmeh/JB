"""Application settings, loaded from environment variables / a .env file."""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

if getattr(sys, "frozen", False):  # PyInstaller executable
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


def _int(name, default):
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return int(default)


def _str(name, default=""):
    value = os.getenv(name)
    return value.strip() if value and value.strip() else default


@dataclass
class Settings:
    languagetool_url: str = field(default_factory=lambda: _str(
        "LANGUAGETOOL_URL", "https://api.languagetool.org/v2/check"))
    language: str = field(default_factory=lambda: _str("LANGUAGETOOL_LANGUAGE", "en-US"))
    languagetool_username: str = field(default_factory=lambda: _str("LANGUAGETOOL_USERNAME"))
    languagetool_api_key: str = field(default_factory=lambda: _str("LANGUAGETOOL_API_KEY"))
    max_chars: int = field(default_factory=lambda: _int("MAX_CHARS", 18000))
    requests_per_minute: int = field(default_factory=lambda: _int("LANGUAGETOOL_REQUESTS_PER_MINUTE", 18))
    chars_per_minute: int = field(default_factory=lambda: _int("LANGUAGETOOL_CHARS_PER_MINUTE", 70000))
    timeout: int = field(default_factory=lambda: _int("LANGUAGETOOL_TIMEOUT", 60))
    max_retries: int = field(default_factory=lambda: _int("LANGUAGETOOL_MAX_RETRIES", 4))

    rewrite_provider: str = field(default_factory=lambda: _str("REWRITE_PROVIDER", "none").lower())
    rewrite_model: str = field(default_factory=lambda: _str("REWRITE_MODEL", "claude-opus-5-5"))

    max_upload_mb: int = field(default_factory=lambda: _int("MAX_UPLOAD_MB", 50))
    job_ttl_minutes: int = field(default_factory=lambda: _int("JOB_TTL_MINUTES", 120))
    max_concurrent_jobs: int = field(default_factory=lambda: _int("MAX_CONCURRENT_JOBS", 1))

    input_dir: Path = BASE_DIR / "input"
    output_dir: Path = BASE_DIR / "output"
    temp_dir: Path = BASE_DIR / "temp"
    log_dir: Path = BASE_DIR / "logs"

    def __post_init__(self):
        # The documented LanguageTool limit is 60,000 characters per request.
        self.max_chars = max(1000, min(self.max_chars, 60000))


# Backwards-compatible module-level names.
_default = Settings()
LANGUAGETOOL_URL = _default.languagetool_url
LANGUAGE = _default.language
MAX_CHARS = _default.max_chars


def get_settings():
    return Settings()
