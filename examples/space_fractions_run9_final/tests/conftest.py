import os
import tempfile
from pathlib import Path

import pytest

SEED_JSON = Path("data/questions_seed.json").read_text(encoding="utf-8")


@pytest.fixture
def seed_json():
    return SEED_JSON


@pytest.fixture
def tmp_store(seed_json):
    from store.store import QuestionStore
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    st = QuestionStore(Path(path), seed_json=seed_json)
    yield st
    st.close()
    try:
        os.remove(path)
    except OSError:
        pass
