"""Game scoring and flow tests."""
import pytest

from game.game import Game, stars_for_percentage
from game.state_machine import GameState, StateError
from questions.question import Question


def _questions(n=10):
    return [Question(id=f"q{i}", prompt=f"What is {i}/4?", answer="1/2")
            for i in range(n)]


def test_view_score_initial():
    g = Game(_questions())
    assert g.viewScore() == 0


def test_correct_answer_increments_score():
    g = Game(_questions())
    assert g.submit_answer("1/2") is True
    assert g.score == 1


def test_equivalent_fraction_accepted():
    g = Game(_questions())
    assert g.submit_answer("2/4") is True


def test_wrong_answer_does_not_increment():
    g = Game(_questions())
    assert g.submit_answer("3/4") is False
    assert g.score == 0


def test_finishes_and_game_over():
    g = Game(_questions(n=2))
    g.submit_answer("1/2")
    g.submit_answer("1/2")
    assert g.is_finished()
    assert g.state is GameState.GAME_OVER
    assert g.percentage() == 100.0


def test_submit_after_finished_raises():
    g = Game(_questions(n=1))
    g.submit_answer("1/2")
    with pytest.raises(StopIteration):
        g.submit_answer("1/2")


def test_submit_while_game_over_raises():
    g = Game(_questions(n=3))
    g.game_over()
    with pytest.raises(StateError):
        g.submit_answer("1/2")


def test_percentage_and_stars():
    g = Game(_questions(n=4))
    g.submit_answer("1/2")  # correct
    g.submit_answer("9/9")  # wrong
    g.submit_answer("1/2")  # correct
    g.submit_answer("9/9")  # wrong
    assert g.percentage() == 50.0
    assert g.stars() == 1


def test_stars_for_percentage():
    assert stars_for_percentage(95) == 3
    assert stars_for_percentage(90) == 3
    assert stars_for_percentage(75) == 2
    assert stars_for_percentage(50) == 1
    assert stars_for_percentage(30) == 0
