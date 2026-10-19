"""State machine tests (valid + invalid transitions)."""
import random

import pytest

from game.game import Game, InvalidTransition
from game.game_state import GameState
from tests.conftest import make_choice_questions


def _new_game():
    return Game("g", make_choice_questions(3), random.Random(1))


def test_initial_state_is_playing():
    assert _new_game().state is GameState.PLAYING


def test_pause_resume():
    g = _new_game()
    g.pause()
    assert g.state is GameState.PAUSED
    g.resume()
    assert g.state is GameState.PLAYING


def test_gameover():
    g = _new_game()
    g.game_over()
    assert g.state is GameState.GAMEOVER


def test_pause_from_paused_invalid():
    g = _new_game()
    g.pause()
    with pytest.raises(InvalidTransition):
        g.pause()


def test_resume_from_playing_invalid():
    g = _new_game()
    with pytest.raises(InvalidTransition):
        g.resume()


def test_gameover_from_paused_invalid():
    g = _new_game()
    g.pause()
    with pytest.raises(InvalidTransition):
        g.game_over()


def test_play_from_gameover_invalid():
    g = _new_game()
    g.game_over()
    with pytest.raises(InvalidTransition):
        g.play()
