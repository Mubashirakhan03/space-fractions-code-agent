"""User and Admin tests."""
import pytest

from users.admin import Admin
from users.user import User
from questions.question import Question
from tests.conftest import make_choice_questions
from game.game import Game


def test_user_view_score():
    import random
    g = Game("g", make_choice_questions(2), random.Random(1))
    u = User(id="u1", username="kid")
    u.play_game(g)
    assert u.view_score(g) == 0


def test_admin_update_questions(repo):
    admin = Admin(id="a1", username="teacher")
    qs = [Question(id="z1", prompt="New Q", correct="1/2", kind="choice",
                   options=["1/2", "1/4"])]
    admin.update_questions(qs, repo)
    assert repo.count() == 1
    assert repo.get("z1").prompt == "New Q"
