"""Tests for the Game state machine and scoring flow."""
import pytest

from game.game import Game, GameResult
from game.state import GameState, can_transition
from questions.question import Question


def _make_game(questions=None):
    questions = questions or [
        Question(id=str(i), prompt=f"q{i}", answer="1/2")
        for i in range(3)
    ]
    return Game(id="g1", questions=questions)


def test_valid_transitions():
    assert can_transition(GameState.PLAYING, GameState.PAUSED)
    assert can_transition(GameState.PLAYING, GameState.GAMEOVER)
    assert can_transition(GameState.PAUSED, GameState.PLAYING)


def test_invalid_transitions():
    assert not can_transition(GameState.PAUSED, GameState.GAMEOVER)
    assert not can_transition(GameState.GAMEOVER, GameState.PLAYING)
    assert not can_transition(GameState.GAMEOVER, GameState.PAUSED)


def test_pause_resume_flow():
    g = _make_game()
    assert g.state is GameState.PLAYING
    g.pause()
    assert g.state is GameState.PAUSED
    g.resume()
    assert g.state is GameState.PLAYING


def test_invalid_pause_raises():
    g = _make_game()
    g.pause()
    with pytest.raises(ValueError):
        g.pause()


def test_submit_while_paused_raises():
    g = _make_game()
    g.pause()
    with pytest.raises(ValueError):
        g.submit("1/2")


def test_submit_advances_and_scores():
    g = _make_game()
    correct, _ = g.submit("1/2")
    assert correct is True
    assert g.score == 1
    assert g.current_index == 1
    assert g.question_number == 2


def test_wrong_submit_does_not_score():
    g = _make_game()
    correct, _ = g.submit("999/1")
    assert correct is False
    assert g.score == 0


def test_game_over_on_last_question():
    g = _make_game([Question(id="0", prompt="p", answer="1/2")])
    g.submit("1/2")
    assert g.state is GameState.GAMEOVER


def test_result_stars():
    g = _make_game([Question(id=str(i), prompt="p", answer="1/2")
                    for i in range(10)])
    for _ in range(10):
        g.submit("1/2")
    res = g.result()
    assert res.percentage == 100
    assert res.stars == 3
    assert res.score == 10


def test_result_zero_stars():
    g = _make_game([Question(id=str(i), prompt="p", answer="1/2")
                    for i in range(10)])
    for _ in range(10):
        g.submit("999/1")
    res = g.result()
    assert res.percentage == 0
    assert res.stars == 0
