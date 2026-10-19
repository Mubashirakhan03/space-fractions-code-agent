"""Unit tests for Question."""
from questions.question import Question


def test_choice_question_correct_match():
    q = Question(id="1", prompt="Which is 1/2?", correct="1/2", kind="choice",
                 options=["1/2", "1/4"])
    assert q.check_answer("1/2") is True
    assert q.check_answer("1/4") is False


def test_typed_question_accepts_equivalent_fraction():
    q = Question(id="2", prompt="Add", correct="1/2", kind="typed", options=[])
    assert q.check_answer("2/4") is True
    assert q.check_answer("1/3") is False


def test_typed_question_invalid_input_is_false():
    q = Question(id="3", prompt="Add", correct="1/2", kind="typed", options=[])
    assert q.check_answer("banana") is False
    assert q.check_answer("") is False


def test_choice_question_requires_correct_in_options():
    try:
        Question(id="4", prompt="p", correct="9/9", kind="choice", options=["1/2"])
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_get_prompt_and_options():
    q = Question(id="5", prompt="P?", correct="1/2", kind="choice",
                 options=["1/2", "1/4"])
    assert q.get_prompt() == "P?"
    assert q.get_options() == ["1/2", "1/4"]
