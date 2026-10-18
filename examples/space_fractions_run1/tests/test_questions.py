"""Question and answer-checking tests."""
import pytest

from questions.question import Question, VALID_TYPES
from questions.checker import check_answer


def test_question_props():
    q = Question(id="q1", prompt="What is 1/2 + 1/4?", type="add_subtract",
                 options=[], answer="3/4")
    assert q.get_prompt() == "What is 1/2 + 1/4?"
    assert q.get_options() == []
    assert not q.is_multiple_choice()


def test_question_multiple_choice():
    q = Question(id="q2", prompt="Pick 1/2 equivalent", type="equivalent",
                 options=["2/4", "1/3"], answer="2/4")
    assert q.is_multiple_choice()
    assert q.get_options() == ["2/4", "1/3"]


def test_invalid_type_raises():
    with pytest.raises(ValueError):
        Question(id="x", prompt="p", type="bad", options=[], answer="1/2")


def test_valid_types():
    assert VALID_TYPES == {"equivalent", "compare", "add_subtract", "simplify"}


def test_check_equivalent_fractions():
    assert check_answer("1/2", "2/4")
    assert check_answer("1/2", "1/2")
    assert check_answer("3/4", "6/8")
    assert check_answer("2/3", "4/6")


def test_check_incorrect():
    assert not check_answer("1/2", "1/3")
    assert not check_answer("3/4", "1/2")


def test_check_whole_and_decimal():
    assert check_answer("1", "1")
    assert check_answer("1/2", "0.5")


def test_check_empty():
    assert not check_answer("1/2", "")
