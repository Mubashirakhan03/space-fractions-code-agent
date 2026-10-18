"""Shared pytest fixtures."""
import os
import sys

import pytest

# Ensure project root is importable.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def tmp_db(tmp_path):
    return str(tmp_path / "test.db")
