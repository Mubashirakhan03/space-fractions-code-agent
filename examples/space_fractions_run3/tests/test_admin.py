from admin.admin import Admin
from questions.question import Question


def test_admin_update_questions():
    a = Admin(id="a1", username="admin")
    qs = [Question(id="q1", prompt="p", answer="1/2")]
    a.update_questions(qs)
    assert a.questions == qs
