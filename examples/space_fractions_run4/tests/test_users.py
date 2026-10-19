"""Tests for User and Admin entities and their composition links."""
import pytest

from users.user import User
from admin.admin import Admin
from questions.question import Question
from questions.repository import QuestionRepository
from game.game import Game


def test_user_play_and_view_score():
    u = User(id="u1", username="mia")
    g = Game(id="g1", questions=[Question(id="0", prompt="p", answer="1/2")])
    u.playGame(g)
    assert g.state.value == "Playing"
    g.submit("1/2")
    assert u.viewScore(g) == 1


def test_admin_authenticate():
    a = Admin(id="a1", passcode="secret")
    assert a.authenticate("secret") is True
    assert a.authenticate("wrong") is False


def test_admin_update_questions(tmp_path):
    data = tmp_path / "q.json"
    data.write_text("[]", encoding="utf-8")
    repo = QuestionRepository(data_file=data)
    repo._questions = []
    a = Admin(id="a1", repository=repo)
    new = [Question(id="1", prompt="p", answer="1/2"),
           Question(id="2", prompt="p", answer="1/3")]
    a.updateQuestions(new)
    assert repo.count() == 2


def test_admin_without_repository_raises():
    a = Admin(id="a1")
    with pytest.raises(ValueError):
        a.updateQuestions([])


def test_admin_add_delete(tmp_path):
    data = tmp_path / "q.json"
    data.write_text("[]", encoding="utf-8")
    repo = QuestionRepository(data_file=data)
    repo._questions = []
    a = Admin(id="a1", repository=repo)
    a.addQuestion(Question(id="9", prompt="p", answer="1/2"))
    assert repo.count() == 1
    assert a.deleteQuestion("9") is True
    assert repo.count() == 0
