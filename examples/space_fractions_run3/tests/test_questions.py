import pytest

from questions.question import Question


def make_question(answer="1/2", options=None, qtype="equivalent", prompt="q"):
    return Question(
        id="q1", prompt=prompt, options=options or [], answer=answer, qtype=qtype,
    )


@pytest.mark.parametrize(
    "given,expected",
    [
        ("2/4", "1/2"),
        ("1/2", "1/2"),
        ("0.5", "1/2"),
        ("4/8", "1/2"),
    ],
)
def test_equivalent_fractions_accepted(given, expected):
    q = make_question(answer=expected)
    assert q.check_answer(given) is True


def test_wrong_fraction_rejected():
    q = make_question(answer="1/2")
    assert q.check_answer("1/3") is False


def test_multiple_choice_matches_option():
    q = make_question(answer="2/4", options=["2/4", "1/3"])
    assert q.check_answer("2/4") is True
    assert q.check_answer("1/3") is False


def test_word_comparison_case_insensitive():
    q = make_question(answer="greater", qtype="compare")
    assert q.check_answer("Greater") is True
    assert q.check_answer("less") is False


def test_blank_answer_rejected():
    q = make_question(answer="1/2")
    assert q.check_answer("") is False
    assert q.check_answer("   ") is False


def test_get_prompt_and_options():
    q = make_question(options=["a", "b"], prompt="Which one?")
    assert q.get_prompt() == "Which one?"
    assert q.get_options() == ["a", "b"]
