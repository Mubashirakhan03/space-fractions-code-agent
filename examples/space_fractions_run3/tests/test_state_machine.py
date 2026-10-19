import pytest

from game.game import Game
from game.game_state import GameState, GameStateError, transition
from questions.question import Question


def make_question(answer="1/2"):
    return Question(id="q1", prompt="p", options=[], answer=answer)


def test_valid_transitions():
    assert transition(None, "start") == GameState.PLAYING
    assert transition(GameState.PLAYING, "pause") == GameState.PAUSED
    assert transition(GameState.PAUSED, "resume") == GameState.PLAYING
    assert transition(GameState.PLAYING, "game_over") == GameState.GAME_OVER


def test_invalid_transitions_raise():
    with pytest.raises(GameStateError):
        transition(GameState.GAME_OVER, "pause")
    with pytest.raises(GameStateError):
        transition(GameState.PAUSED, "game_over")
    with pytest.raises(GameStateError):
        transition(GameState.GAME_OVER, "resume")


def test_submit_while_paused_raises():
    g = Game(id="g1", questions=[make_question()])
    g.pause()
    with pytest.raises(GameStateError):
        g.submit_answer("1/2")
