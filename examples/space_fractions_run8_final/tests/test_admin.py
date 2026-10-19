from admin.admin import Admin
from question.question import Question


def test_update_questions():
    a = Admin()
    q1 = Question("p1", ["a", "b"], 0)
    q2 = Question("p2", ["c", "d"], 0)
    a.updateQuestions([q1, q2])
    assert len(a.questions) == 2


def test_add_question():
    a = Admin()
    q = Question("p", ["a", "b"], 0)
    a.addQuestion(q)
    assert a.questions == [q]
