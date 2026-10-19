from game.game import Game
from game.state import GameState
from question.question import Question, QuestionKind


def _q(prompt, options, ci=0):
    return Question(prompt, options, ci)


def test_score_updates_and_rating():
    qs = [_q("Which equals 1/2?", ["2/4", "1/3", "2/5", "3/4"]),
          _q("Which equals 1/3?", ["2/6", "1/2", "3/4", "1/4"])]
    g = Game(qs)
    assert g.viewScore() == 0
    assert g.submit("2/4") is True
    assert g.score == 1
    assert g.submit("1/2") is False
    assert g.score == 1
    assert g.is_over
    assert g.state_machine.state == GameState.GAMEOVER
    assert g.rating().startswith("Good") or "Great" in g.rating() or \
        g.rating() == "Excellent! You are a fractions star!"


def test_zero_score_rating_not_praising():
    qs = [_q("Which equals 1/2?", ["2/4", "1/3", "2/5", "3/4"])]
    g = Game(qs)
    g.submit("1/3")  # wrong
    assert g.score == 0
    r = g.rating()
    assert "Excellent" not in r
    assert "Great" not in r
    assert "Good" not in r


def test_play_and_view_score_api():
    g = Game([_q("x", ["a", "b"], 0)])
    g.play()
    assert g.viewScore() == 0


def test_submit_past_end_raises():
    import pytest
    g = Game([_q("x", ["a", "b"], 0)])
    g.submit("a")
    with pytest.raises(IndexError):
        g.submit("a")
