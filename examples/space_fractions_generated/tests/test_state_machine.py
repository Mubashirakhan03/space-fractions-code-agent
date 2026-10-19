"""State machine tests: valid and invalid transitions."""
import pytest

from game.state_machine import GameState, GameStateMachine, StateError


def test_initial_state_playing():
    sm = GameStateMachine()
    assert sm.state is GameState.PLAYING


def test_pause_resume_cycle():
    sm = GameStateMachine()
    sm.pause()
    assert sm.state is GameState.PAUSED
    sm.resume()
    assert sm.state is GameState.PLAYING


def test_playing_to_game_over():
    sm = GameStateMachine()
    sm.game_over()
    assert sm.state is GameState.GAME_OVER


def test_paused_to_game_over():
    sm = GameStateMachine()
    sm.pause()
    sm.game_over()
    assert sm.state is GameState.GAME_OVER


def test_resume_from_playing_invalid():
    sm = GameStateMachine()
    with pytest.raises(StateError):
        sm.resume()


def test_pause_from_game_over_invalid():
    sm = GameStateMachine()
    sm.game_over()
    with pytest.raises(StateError):
        sm.pause()


def test_game_over_from_game_over_invalid():
    sm = GameStateMachine()
    sm.game_over()
    with pytest.raises(StateError):
        sm.game_over()


def test_resume_from_game_over_invalid():
    sm = GameStateMachine()
    sm.game_over()
    with pytest.raises(StateError):
        sm.resume()
