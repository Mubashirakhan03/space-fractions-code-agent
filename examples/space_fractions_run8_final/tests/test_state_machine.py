import pytest

from game.state import GameState, GameStateMachine, InvalidTransition


def test_initial_playing():
    sm = GameStateMachine()
    assert sm.state == GameState.PLAYING


def test_pause_resume():
    sm = GameStateMachine()
    sm.pause()
    assert sm.state == GameState.PAUSED
    sm.resume()
    assert sm.state == GameState.PLAYING


def test_game_over():
    sm = GameStateMachine()
    sm.game_over()
    assert sm.state == GameState.GAMEOVER


def test_pause_then_game_over():
    sm = GameStateMachine()
    sm.pause()
    sm.game_over()
    assert sm.state == GameState.GAMEOVER


def test_invalid_transitions():
    sm = GameStateMachine()
    with pytest.raises(InvalidTransition):
        sm.resume()          # can't resume from Playing
    sm.game_over()
    with pytest.raises(InvalidTransition):
        sm.pause()           # can't pause a finished game
    with pytest.raises(InvalidTransition):
        sm.resume()


def test_can_queries():
    sm = GameStateMachine()
    assert sm.can("pause")
    assert not sm.can("resume")
    assert sm.can("game_over")
