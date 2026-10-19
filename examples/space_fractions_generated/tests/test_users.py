"""User and Admin tests."""
from admin.admin import Admin
from game.game import Game
from questions.question import Question
from questions.repository import QuestionRepository
from users.user import User


def test_user_play_and_score(tmp_path):
    db = str(tmp_path / "t.db")
    repo = QuestionRepository(db_path=db)
    qs = [Question(id="q1", prompt="p", answer="1/2")]
    u = User("Alice")
    g = Game(qs, player_name="Alice", question_count=1)
    u.playGame(g)
    assert u.username == "Alice"
    assert len(u.games) == 1
    g.submit_answer("1/2")
    assert u.viewScore(g) == 1


def test_admin_update_questions(tmp_path):
    db = str(tmp_path / "t.db")
    repo = QuestionRepository(db_path=db)
    admin = Admin(repository=repo)
    q = Question(id="q42", prompt="new", answer="1/3")
    admin.updateQuestions([q])
    questions = admin.list_questions()
    assert any(x.id == "q42" for x in questions)


def test_admin_delete(tmp_path):
    db = str(tmp_path / "t.db")
    repo = QuestionRepository(db_path=db)
    admin = Admin(repository=repo)
    admin.add_question(Question(id="qx", prompt="x", answer="1/2"))
    admin.delete_question("qx")
    assert all(x.id != "qx" for x in admin.list_questions())
