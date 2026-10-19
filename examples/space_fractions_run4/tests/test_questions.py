"""Tests for Question entity, answer checking and repository."""
from fractions import Fraction

from questions.question import Question, QuestionType
from questions.repository import QuestionRepository


def test_get_prompt_and_options():
    q = Question(id="q1", prompt="Simplify 4/8?", options=["1/2", "2/3"],
                 answer="1/2")
    assert q.getPrompt() == "Simplify 4/8?"
    assert q.getOptions() == ["1/2", "2/3"]


def test_equivalent_fractions_accepted():
    q = Question(id="q1", prompt="2/4 = ?", answer="1/2",
                 qtype=QuestionType.EQUIVALENT, is_choice=False)
    assert q.checkAnswer("2/4")[0] is True
    assert q.checkAnswer("1/2")[0] is True
    assert q.checkAnswer("3/4")[0] is False


def test_wrong_answer_returns_expected_value():
    q = Question(id="q1", prompt="?", answer="3/4", is_choice=False)
    correct, expected = q.checkAnswer("1/2")
    assert correct is False
    assert expected == "3/4"


def test_compare_type_uses_string_match():
    q = Question(id="q1", prompt="larger?", options=["3/4", "1/2"],
                 answer="3/4", qtype=QuestionType.COMPARE, is_choice=True)
    assert q.checkAnswer("3/4")[0] is True
    assert q.checkAnswer("1/2")[0] is False


def test_invalid_input_not_crash():
    q = Question(id="q1", prompt="?", answer="1/2", is_choice=False)
    correct, expected = q.checkAnswer("abc")
    assert correct is False
    assert expected == "1/2"


def test_repository_loads_seed_questions():
    repo = QuestionRepository()
    assert repo.count() >= 20
    types = {q.qtype.value for q in repo.all()}
    assert {"equivalent", "compare", "add_subtract", "simplify"} <= types


def test_repository_sample_size():
    repo = QuestionRepository()
    sample = repo.sample(10)
    assert len(sample) == 10

def test_repository_add_update_delete(tmp_path):
    data = tmp_path / "q.json"
    data.write_text("[]", encoding="utf-8")
    repo = QuestionRepository(data_file=data)
    repo._questions = []
    q = Question(id="1", prompt="p", answer="1/2")
    repo.add(q)
    assert repo.count() == 1
    repo.update(Question(id="1", prompt="p2", answer="2/4"))
    assert repo.get("1").prompt == "p2"
    assert repo.delete("1") is True
    assert repo.delete("missing") is False
