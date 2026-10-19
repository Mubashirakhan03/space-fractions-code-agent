"""Question model and answer-checking tests."""
from fractions import Fraction

from questions.question import Question, QType


def test_get_prompt_and_options():
    q = Question(id="q", prompt="Which is 1/2?", answer="1/2",
                 options=["1/2", "1/3"])
    assert q.getPrompt() == "Which is 1/2?"
    assert q.getOptions() == ["1/2", "1/3"]


def test_equivalent_fraction_equality():
    q = Question(id="q", prompt="p", answer="1/2")
    assert q.is_correct("2/4")
    assert q.is_correct("1/2")
    assert not q.is_correct("1/3")


def test_integer_answer():
    q = Question(id="q", prompt="p", answer="1")
    assert q.is_correct("1")
    assert q.is_correct("2/2")


def test_invalid_input_not_correct():
    q = Question(id="q", prompt="p", answer="1/2")
    assert not q.is_correct("banana")
    assert not q.is_correct("")
    assert not q.is_correct("1/0")


def test_multiple_choice_detection():
    q1 = Question(id="q", prompt="p", answer="1/2", options=["1/2", "1/3"])
    q2 = Question(id="q", prompt="p", answer="1/2")
    assert q1.is_multiple_choice()
    assert not q2.is_multiple_choice()


def test_round_trip_dict():
    q = Question(id="q", prompt="p", answer="2/4", qtype=QType.SIMPLIFY.value,
                 options=["1/2"])
    q2 = Question.from_dict(q.to_dict())
    assert q2.id == "q"
    assert q2.answer == Fraction(1, 2)
    assert q2.qtype is QType.SIMPLIFY
    assert q2.getOptions() == ["1/2"]
