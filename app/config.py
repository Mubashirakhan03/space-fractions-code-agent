"""Application configuration.

Key lookup order: GUI/config.json value → `DEEPSEEK_API_KEY` env var → `.env` (dev mode).
Config lives in %APPDATA%\\SpaceFractionsAgent\\config.json — never in the repo, never logged.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, fields
from pathlib import Path

from app import APP_NAME

ENV_KEY = "DEEPSEEK_API_KEY"


@dataclass
class AppConfig:
    api_key: str = ""
    provider: str = "deepseek"  # "deepseek" or "mock"
    thinking: bool = False
    max_steps: int = 60  # agent loop iterations
    max_requests: int = 40  # LLM calls per run
    max_cost_usd: float = 1.00
    max_total_tokens: int = 2_000_000
    max_output_tokens: int = 32768  # a write_files batch of several modules needs more than 8K
    fix_rounds: int = 3  # verify → fix cycles
    ask_before_write: bool = False
    doc_path: str = ""
    view_path: str = ""
    output_dir: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> AppConfig:
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})

    def resolved_api_key(self) -> str:
        """Key from config, else environment (including a dev `.env`)."""
        if self.api_key:
            return self.api_key
        load_dotenv_if_present()
        return os.environ.get(ENV_KEY, "")


def config_dir() -> Path:
    base = os.environ.get("APPDATA") or str(Path.home() / ".config")
    return Path(base) / APP_NAME


def load_config(path: Path | None = None) -> AppConfig:
    path = path or config_dir() / "config.json"
    if not path.exists():
        return AppConfig()
    try:
        return AppConfig.from_dict(json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, TypeError):
        return AppConfig()


def save_config(cfg: AppConfig, path: Path | None = None) -> Path:
    path = path or config_dir() / "config.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(cfg), indent=2), encoding="utf-8")
    return path


def mask_key(key: str) -> str:
    """Safe representation for logs/UI: never shows more than the last 4 characters."""
    if not key:
        return "(not set)"
    return "****" + key[-4:] if len(key) > 8 else "****"


def load_dotenv_if_present() -> None:
    """Load `.env` from the working directory or project root (dev mode only, no override)."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    for candidate in (Path.cwd() / ".env", Path(__file__).resolve().parent.parent / ".env"):
        if candidate.exists():
            load_dotenv(candidate, override=False)
            return
