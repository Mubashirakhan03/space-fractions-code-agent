import pytest

from game.state_machine import GameStateMachine, State, InvalidTransitionError


def test_initial_state_is_playing():
    sm = GameStateMachine()
    assert sm.state is State.PLAYING


def test_initial_transition_star_to_playing():
    sm = GameStateMachine(State.PLAYING)
    assert sm.state is State.PLAYING


def test_pause_then_resume():
    sm = GameStateMachine()
    sm.pause()
    assert sm.state is State.PAUSED
    sm.resume()
    assert sm.state is State.PLAYING


def test_game_over():
    sm = GameStateMachine()
    sm.game_over()
    assert sm.state is State.GAME_OVER


def test_invalid_pause_from_gameover():
    sm = GameStateMachine()
    sm.game_over()
    with pytest.raises(InvalidTransitionError):
        sm.pause()


def test_invalid_resume_from_playing():
    sm = GameStateMachine()
    with pytest.raises(InvalidTransitionError):
        sm.resume()


def test_invalid_gamer_over_from_paused():
    sm = GameStateMachine()
    sm.pause()
    with pytest.raises(InvalidTransitionError):
        sm.game_over()


def test_transition_dispatch():
    sm = GameStateMachine()
    assert sm.transition("pause") is State.PAUSED
    assert sm.transition("resume") is State.PLAYING
    assert sm.transition("gameOver") is State.GAME_OVER


def test_unknown_trigger():
    sm = GameStateMachine()
    with pytest.raises(InvalidTransitionError):
        sm.transition("bogus")
