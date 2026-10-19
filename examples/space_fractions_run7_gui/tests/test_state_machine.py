"""State machine tests: valid AND invalid transitions."""
import pytest

from game.state import GameState, GameStateMachine


def test_initial_state_is_playing():
    sm = GameStateMachine()
    assert sm.state is GameState.PLAYING


def test_pause_and_resume():
    sm = GameStateMachine()
    sm.pause()
    assert sm.state is GameState.PAUSED
    sm.resume()
    assert sm.state is GameState.PLAYING


def test_game_over():
    sm = GameStateMachine()
    sm.gameOver()
    assert sm.state is GameState.GAMEOVER


def test_gameover_is_terminal():
    sm = GameStateMachine()
    sm.gameOver()
    with pytest.raises(ValueError):
        sm.pause()
    with pytest.raises(ValueError):
        sm.resume()


def test_invalid_transition_from_gameover():
    sm = GameStateMachine()
    sm.gameOver()
    with pytest.raises(ValueError):
        sm.resume()  # cannot resume from GameOver
    with pytest.raises(ValueError):
        sm.transition(GameState.PLAYING)


def test_playing_to_gameover_is_valid():
    sm = GameStateMachine()
    sm.gameOver()  # Playing -> GameOver is an allowed transition
    assert sm.state is GameState.GAMEOVER
