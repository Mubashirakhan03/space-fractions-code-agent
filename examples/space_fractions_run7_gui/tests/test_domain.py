"""Domain logic tests: entities, round building, service sequence."""
import random

from admin.admin import Admin
from game.game import Game
from game.round import build_round
from game.service import GameService
from question.question import Question, QuestionKind
from user.user import User


def make_q(qid="q1", correct="1/2", options=None, kind=QuestionKind.COMPARE):
    return Question(id=qid, prompt="What is it?", correct=correct,
                    options=list(options or []), kind=kind)


def test_question_getters():
    q = make_q(options=["1/4", "1/2"])
    assert q.getPrompt() == "What is it?"
    assert q.getOptions() == ["1/4", "1/2"]


def test_question_normalisation():
    q = make_q(correct="2/4")
    assert q.checkAnswer("1/2")
    assert q.checkAnswer("2/4")
    assert not q.checkAnswer("1/3")


def test_question_validation_requires_fields():
    q = Question(id="", prompt="", correct="", options=[], kind=QuestionKind.COMPARE)
    errors = q.validate()
    assert any("ID" in e for e in errors)
    assert any("Prompt" in e for e in errors)
    assert any("Correct" in e for e in errors)


def test_question_validation_duplicate_options():
    q = Question(id="x", prompt="p", correct="1/2",
                 options=["1/2", "2/4"], kind=QuestionKind.EQUIVALENT)
    assert any("Duplicate" in e for e in q.validate())


def test_game_score_and_finish():
    questions = [make_q("a", "1/2"), make_q("b", "1/3")]
    g = Game(id="g1", questions=questions)
    assert g.total == 2
    assert g.current_question.id == "a"
    assert g.submitAnswer("1/2") is True
    assert g.submitAnswer("1/4") is False
    assert g.viewScore() == 1
    assert g.is_finished


def test_user_composition():
    u = User(id="u1", username="kid")
    g = Game(id="g1", questions=[make_q()])
    u.playGame(g)
    assert u.current_game is g
    assert u.viewScore(g) == 0


def test_admin_update_questions():
    ad = Admin(id="a1", username="teacher")
    ad.updateQuestions([make_q("a"), make_q("b")])
    assert len(ad.questions) == 2
    errors = ad.addQuestion(make_q("c"))
    assert errors == []
    assert len(ad.questions) == 3


def test_build_round_random_and_shuffled():
    pool = [make_q(f"p{i}") for i in range(25)]
    r1 = build_round(pool, total=10, generated_count=5, rng=random.Random(1))
    r2 = build_round(pool, total=10, generated_count=5, rng=random.Random(2))
    assert len(r1) == 10
    assert len(r2) == 10
    assert [q.id for q in r1] != [q.id for q in r2]


def test_service_sequence_result_before_advance():
    pool = [make_q("q1", correct="1/2", options=["1/3", "1/2"])]
    svc = GameService(pool=pool, default_total=1)
    svc.play()
    q = svc.current_question()
    assert q is not None
    # submit a definitely-wrong answer for whatever question was served
    wrong = "999999999999/1"
    result = svc.submit(wrong)
    assert result.correct is False
    assert result.expected == q.correct
    assert result.submitted == wrong
    assert result.prompt == q.prompt
