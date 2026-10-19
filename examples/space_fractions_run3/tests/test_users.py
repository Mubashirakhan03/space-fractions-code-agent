from users.user import User
from game.game import Game
from questions.question import Question


def test_user_play_game_and_view_score():
    u = User(id="u1", username="kid")
    g = Game(id="g1", questions=[Question(id="q", prompt="p", answer="1/2")])
    u.play_game(g)
    assert len(u.games) == 1
    g.submit_answer("1/2")
    assert u.view_score(g) == 100
