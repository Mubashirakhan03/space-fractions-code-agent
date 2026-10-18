"""Admin tests: PIN verification and question update (SequenceDiagram2)."""
from admin import Admin
from questions import Question, QuestionRepository


def test_verify_pin():
    assert Admin.verify_pin("space-admin")
    assert not Admin.verify_pin("wrong")


def test_add_question(tmp_db):
    repo = QuestionRepository(tmp_db, seed_path=None)
    admin = Admin()
    q = Question(id="a1", prompt="prompt", type="simplify", options=[], answer="1/2")
    admin.add_question(repo, q)
    assert repo.get("a1") is not None
    repo.close()


def test_update_questions(tmp_db):
    repo = QuestionRepository(tmp_db, seed_path=None)
    admin = Admin()
    qs = [Question(id="a1", prompt="p1", type="simplify", options=[], answer="1/2"),
          Question(id="a2", prompt="p2", type="compare", options=["1/2", "1/3"], answer="1/2")]
    admin.update_questions(repo, qs)
    assert repo.get("a1") is not None
    assert repo.get("a2") is not None
    repo.close()


def test_delete_question(tmp_db):
    repo = QuestionRepository(tmp_db, seed_path=None)
    admin = Admin()
    q = Question(id="a1", prompt="p", type="simplify", options=[], answer="1/2")
    admin.add_question(repo, q)
    admin.delete_question(repo, "a1")
    assert repo.get("a1") is None
    repo.close()
