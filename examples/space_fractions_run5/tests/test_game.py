"""Tests for GameController and the Game model."""
import random

import pytest

from game.controller import GameController
from game.models import Game
from game.state_machine import InvalidTransitionError
from questions.model import Question


def _make_questions(n=3):
    return [Question(prompt=f"q{i}", answer="1/2", id=f"q{i}")
            for i in range(n)]


def test_controller_selects_round_size():
    qs = _make_questions(20)
    ctl = GameController(qs, round_size=10, rng=random.Random(1))
    assert ctl.game.total == 10
    assert len(ctl.game.questions) == 10


def test_controller_round_smaller_when_few_questions():
    qs = _make_questions(3)
    ctl = GameController(qs, round_size=10, rng=random.Random(1))
    assert ctl.game.total == 3


def test_submit_correct_increments_score():
    qs = _make_questions(3)
    ctl = GameController(qs, round_size=3, rng=random.Random(1))
    ok, expected = ctl.submit_answer("1/2")
    assert ok
    assert expected == "1/2"
    assert ctl.game.score == 1
    assert ctl.game.correct_count == 1


def test_submit_wrong_does_not_increment():
    qs = _make_questions(3)
    ctl = GameController(qs, round_size=3, rng=random.Random(1))
    ok, expected = ctl.submit_answer("9/10")
    assert not ok
    assert ctl.game.score == 0


def test_game_over_after_all_questions():
    qs = _make_questions(2)
    ctl = GameController(qs, round_size=2, rng=random.Random(1))
    assert not ctl.is_finished
    ctl.submit_answer("1/2")
    ctl.advance()
    ctl.submit_answer("1/2")
    ctl.advance()
    assert ctl.is_finished
    assert ctl.state_machine.is_game_over


def test_submit_after_game_over_raises():
    qs = _make_questions(1)
    ctl = GameController(qs, round_size=1, rng=random.Random(1))
    ctl.submit_answer("1/2")
    ctl.advance()
    with pytest.raises(InvalidTransitionError):
        ctl.submit_answer("1/2")


def test_percentage_and_stars():
    g = Game()
    g.answered_count = 10
    g.correct_count = 9
    g.score = 9
    assert g.percentage == 90.0
    assert g.stars() == 3


def test_stars_thresholds():
    g = Game()
    g.answered_count = 10
    g.correct_count = 6
    assert g.stars() == 2
    g.correct_count = 1
    assert g.stars() == 1
    g.correct_count = 0
    assert g.stars() == 0


def test_view_score():
    g = Game()
    g.score = 5
    assert g.viewScore() == 5
