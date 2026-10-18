"""State machine tests: valid and invalid transitions."""
import pytest

from game.state import GameState, InvalidTransitionError, can_transition
from game.game import Game


def test_initial_state_is_playing():
    g = Game()
    assert g.state is GameState.PLAYING


def test_valid_transitions():
    assert can_transition(None, GameState.PLAYING)
    assert can_transition(GameState.PLAYING, GameState.PAUSED)
    assert can_transition(GameState.PAUSED, GameState.PLAYING)
    assert can_transition(GameState.PLAYING, GameState.GAME_OVER)


def test_pause_resume():
    g = Game()
    g.pause()
    assert g.state is GameState.PAUSED
    g.resume()
    assert g.state is GameState.PLAYING


def test_game_over():
    g = Game()
    g.game_over()
    assert g.state is GameState.GAME_OVER


def test_invalid_pause_from_game_over():
    g = Game()
    g.game_over()
    with pytest.raises(InvalidTransitionError):
        g.pause()


def test_invalid_resume_from_playing():
    g = Game()
    with pytest.raises(InvalidTransitionError):
        g.resume()


def test_invalid_game_over_from_paused():
    g = Game()
    g.pause()
    with pytest.raises(InvalidTransitionError):
        g.game_over()


def test_no_transition_from_game_over():
    assert not can_transition(GameState.GAME_OVER, GameState.PLAYING)
    assert not can_transition(GameState.GAME_OVER, GameState.PAUSED)
