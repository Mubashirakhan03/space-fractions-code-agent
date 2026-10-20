from fractions import Fraction

from question.question import Question


def test_get_prompt():
    q = Question(id="q1", prompt="What is 1/2?", choices=["1/2", "1/3"], correct_value="1/2")
    assert q.get_prompt() == "What is 1/2?"


def test_get_options():
    q = Question(id="q1", prompt="p", choices=["1/2", "1/3"], correct_value="1/2")
    assert q.get_options() == ["1/2", "1/3"]


def test_check_choice_answer_correct():
    q = Question(id="q1", prompt="p", choices=["1/2", "1/3"], correct_value="1/2")
    assert q.check_answer("1/2") is True
    assert q.check_answer("1/3") is False


def test_typed_answer_accepts_reduced_only():
    q = Question(id="q1", prompt="Reduce 2/4", kind="reduce",
                 correct_value="1/2", choices=[])
    assert q.check_answer("1/2") is True
    assert q.check_answer("2/4") is False  # not lowest terms


def test_typed_answer_normalises_fraction():
    q = Question(id="q1", prompt="p", kind="add", correct_value="3/4", choices=[])
    assert q.check_answer("3/4") is True
    # addition accepts an equivalent fraction as equal in value
    assert q.check_answer("6/8") is True
    assert q.check_answer("1/2") is False


def test_reduce_is_strict_typed():
    q = Question(id="q1", prompt="Reduce 6/8", kind="reduce",
                 correct_value="3/4", choices=[])
    assert q.check_answer("3/4") is True
    assert q.check_answer("6/8") is False
    assert q.check_answer("12/16") is False


def test_empty_and_blank_answers_rejected():
    q = Question(id="q1", prompt="p", correct_value="1/2", choices=[])
    assert q.check_answer("") is False
    assert q.check_answer("   ") is False
