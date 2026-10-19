from fractions import Fraction
from question.question import Question, QuestionKind


def _parse(s):
    if "/" in s:
        n, d = s.split("/")
        return Fraction(int(n), int(d))
    return Fraction(int(s))


def test_accessors():
    q = Question("Which equals 1/2?", ["2/4", "1/3", "2/5", "3/4"], 0)
    assert q.getPrompt() == "Which equals 1/2?"
    assert q.getOptions() == ["2/4", "1/3", "2/5", "3/4"]
    assert q.correct_answer == "2/4"


def test_check_correct_and_wrong():
    q = Question("Which equals 1/2?", ["2/4", "1/3", "2/5", "3/4"], 0)
    assert q.checkAnswer("2/4") is True
    assert q.checkAnswer("1/3") is False


def test_equivalent_accepts_value_equal():
    q = Question("Which equals 1/2?", ["2/4", "1/3", "2/5", "3/4"], 0,
                 kind=QuestionKind.EQUIVALENT)
    # 4/8 is value-equal to 2/4
    assert q.checkAnswer("4/8") is True


def test_decimal_accepts_equal_value():
    q = Question("1/2 as decimal?", ["0.5", "0.2", "0.25", "0.1"], 0,
                 kind=QuestionKind.DECIMAL)
    assert q.checkAnswer("0.5") is True
    assert q.checkAnswer("0.50") is True
    assert q.checkAnswer("0.2") is False


def test_invalid_correct_index_raises():
    import pytest
    with pytest.raises(ValueError):
        Question("x", ["a", "b"], 5)


def test_roundtrip_dict():
    q = Question("Which equals 1/2?", ["2/4", "1/3"], 0,
                 kind=QuestionKind.EQUIVALENT, explanation="hi")
    d = q.to_dict()
    q2 = Question.from_dict(d)
    assert q2.prompt == q.prompt
    assert q2.correct_answer == "2/4"
    assert q2.correct_index == 0
