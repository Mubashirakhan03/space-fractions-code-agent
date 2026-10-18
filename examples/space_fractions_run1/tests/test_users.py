"""User domain tests."""
from users import User
from game.game import Game


def test_user_props():
    u = User(username="kid", user_id="u1")
    assert u.username == "kid"
    assert u.id == "u1"


def test_play_game_sets_state():
    u = User(username="kid")
    g = Game()
    g.game_over()
    u.play_game(g)
    from game.state import GameState
    assert g.state is GameState.PLAYING


def test_view_score():
    u = User(username="kid")
    g = Game()
    g.record_answer(True)
    g.record_answer(True)
    assert u.view_score(g) == 2
    assert u.view_score() == 0  # no current game set
