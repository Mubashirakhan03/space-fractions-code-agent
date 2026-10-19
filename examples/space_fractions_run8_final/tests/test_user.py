from game.game import Game
from question.question import Question
from user.user import User


def test_play_and_score():
    u = User("alice")
    g = Game([Question("Which equals 1/2?", ["2/4", "1/3"], 0)])
    u.playGame(g)
    assert len(u.games) == 1
    g.submit("2/4")
    assert u.viewScore(g) == 1
