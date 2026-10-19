"""Shared fixtures. Tests never call the real DeepSeek API (zero-cost policy, DECISIONS D-010)."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "samples"


@pytest.fixture(autouse=True)
def _no_real_key(monkeypatch):
    """Hide any real key from the environment so no test can spend credit by accident."""
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setattr("sfagent.config.load_dotenv_if_present", lambda: None)


@pytest.fixture
def doc_path() -> Path:
    return SAMPLES / "Architecture_Documentation.md"


@pytest.fixture
def view_path() -> Path:
    return SAMPLES / "Architecture_View.md"
