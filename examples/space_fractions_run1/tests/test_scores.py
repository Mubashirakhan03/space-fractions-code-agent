"""Score repository additional tests (View Score use case)."""
from users import ScoreRepository


def test_limit_high_scores(tmp_db):
    sr = ScoreRepository(tmp_db)
    for i in range(15):
        sr.add_score(f"user{i}", 5, 10, 50.0 + i, 1)
    rows = sr.high_scores(10)
    assert len(rows) == 10
    sr.close()


def test_empty_scores(tmp_db):
    sr = ScoreRepository(tmp_db)
    assert sr.high_scores() == []
    sr.close()
