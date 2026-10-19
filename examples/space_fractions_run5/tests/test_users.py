"""Tests for User and Admin domain objects."""
from game.models import Game
from users.model import User
from admin.service import Admin
from questions.model import Question


def test_user_play_game_and_view_score():
    u = User("alice")
    g = Game()
    g.score = 4
    u.playGame(g)
    assert u.viewScore(g) == 4
    assert u.username == "alice"


def test_admin_update_questions():
    a = Admin()
    qs = [Question(prompt="p", answer="a", id="x")]
    a.updateQuestions(qs)
    assert [q.id for q in a.questions] == ["x"]


def test_admin_add_remove_replace():
    a = Admin()
    q = Question(prompt="p", answer="a", id="x")
    a.add_question(q)
    assert len(a.questions) == 1
    assert a.remove_question("x")
    assert a.questions == []
    assert not a.remove_question("x")


def test_admin_replace_question():
    a = Admin()
    q = Question(prompt="old", answer="a", id="x")
    a.add_question(q)
    q2 = Question(prompt="new", answer="b", id="x")
    a.replace_question(q2)
    assert a.questions[0].prompt == "new"
