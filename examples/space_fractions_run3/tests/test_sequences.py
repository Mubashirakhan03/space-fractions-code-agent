"""Sequence tests: SequenceDiagram1 (play -> prompt -> submit -> result),
SequenceDiagram2 (Admin -> updateQuestions) and the activity diagram flow."""
from admin.admin import Admin
from game.game_service import GameService
from questions.question import Question


def test_play_flow_sequence():
    q = Question(id="q1", prompt="What is 1/2 + 1/4?", options=["3/4", "2/6"], answer="3/4")
    svc = GameService(game_id="g1", questions=[q])
    game = svc.play()
    assert svc.view_score() == 0
    assert svc.current_prompt() == "What is 1/2 + 1/4?"
    assert svc.current_options() == ["3/4", "2/6"]
    assert svc.submit("3/4") is True
    assert svc.view_score() == 100


def test_wrong_answer_sequence():
    q = Question(id="q1", prompt="p", options=["3/4"], answer="3/4")
    svc = GameService(game_id="g1", questions=[q])
    svc.play()
    result = svc.submit("2/6")
    assert result is False
    assert svc.view_score() == 0


def test_admin_update_questions_sequence():
    a = Admin(id="a1", username="admin")
    q = Question(id="q1", prompt="p", answer="1/2")
    a.update_questions([q])
    assert a.questions == [q]
