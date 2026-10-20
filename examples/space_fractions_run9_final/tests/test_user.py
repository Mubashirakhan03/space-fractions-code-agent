from question.question import Question
from game.game import Game
from user.user import User, Admin


def test_user_play_game_adds_game():
    u = User("u1", "alice")
    g = Game("g1")
    u.play_game(g)
    assert g in u.games


def test_user_view_score():
    u = User("u1", "alice")
    g = Game("g1")
    u.play_game(g)
    assert u.view_score(g) == 0


def test_admin_update_questions():
    a = Admin("a1", "admin")
    qs = [Question(id="q1", prompt="p", correct_value="1/2", choices=[])]
    a.update_questions(qs)
    assert a.questions == qs


def test_admin_spec_alias():
    a = Admin("a1")
    qs = [Question(id="q1", prompt="p", correct_value="1/2", choices=[])]
    a.updateQuestions(qs)
    assert len(a.questions) == 1
