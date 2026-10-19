"""Tests for the Game state machine (valid and invalid transitions)."""
import pytest

from game.state_machine import GameStateMachine, InvalidTransitionError, GameState


def test_initial_state_is_playing():
    sm = GameStateMachine()
    assert sm.is_playing
    assert not sm.is_paused
    assert not sm.is_game_over


def test_playing_to_paused():
    sm = GameStateMachine()
    sm.pause()
    assert sm.is_paused


def test_paused_to_playing():
    sm = GameStateMachine()
    sm.pause()
    sm.resume()
    assert sm.is_playing


def test_playing_to_game_over():
    sm = GameStateMachine()
    sm.game_over()
    assert sm.is_game_over


def test_game_over_is_terminal():
    sm = GameStateMachine()
    sm.game_over()
    with pytest.raises(InvalidTransitionError):
        sm.pause()
    with pytest.raises(InvalidTransitionError):
        sm.resume()
    with pytest.raises(InvalidTransitionError):
        sm.game_over()


def test_pause_from_paused_raises():
    sm = GameStateMachine()
    sm.pause()
    with pytest.raises(InvalidTransitionError):
        sm.pause()


def test_resume_without_pause_raises():
    sm = GameStateMachine()
    with pytest.raises(InvalidTransitionError):
        sm.resume()


def test_game_over_from_paused_raises():
    sm = GameStateMachine()
    sm.pause()
    with pytest.raises(InvalidTransitionError):
        sm.game_over()
