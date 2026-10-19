"""Unit tests for the Game class and message correctness."""
import random

import pytest

from game.game import Game, GameOverError, InvalidTransition
from game.game_state import GameState
from tests.conftest import make_choice_questions


def test_play_returns_prompt():
    g = Game("g1", make_choice_questions(2), random.Random(1))
    assert g.play() == "Q0"


def test_score_counts_correct_answers():
    qs = make_choice_questions(2)
    g = Game("g1", qs, random.Random(1))
    assert g.submit_answer("1/2") is True
    assert g.submit_answer("1/4") is False
    assert g.view_score() == 1


def test_round_ends_in_gameover():
    g = Game("g1", make_choice_questions(2), random.Random(1))
    g.submit_answer("1/2")
    g.submit_answer("1/4")
    assert g.state is GameState.GAMEOVER
    with pytest.raises(GameOverError):
        g.current_question


def test_cannot_submit_after_gameover():
    g = Game("g1", make_choice_questions(1), random.Random(1))
    g.submit_answer("1/2")
    assert g.state is GameState.GAMEOVER
    with pytest.raises(InvalidTransition):
        g.submit_answer("1/2")


def test_wrong_answer_does_not_increment_score():
    g = Game("g1", make_choice_questions(1), random.Random(1))
    assert g.submit_answer("wrong") is False
    assert g.view_score() == 0


def test_message_names_expected_value_before_advance():
    """The UI captures q.correct BEFORE submit_answer advances state."""
    qs = make_choice_questions(2)
    g = Game("g1", qs, random.Random(1))
    expected = g.current_question.correct  # capture before submit
    assert expected == "1/2"
    g.submit_answer("1/4")  # wrong answer for Q0
    # next question should be Q1 (the round advanced), not Q0
    assert g.current_question.prompt == "Q1"
