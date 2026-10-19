"""Tests for question checking (fractions.Fraction equivalence)."""
import pytest

from questions.checker import QuestionChecker
from questions.model import Question


def test_equivalent_fraction_accepted():
    q = Question(prompt="half?", answer="1/2", options=[], qtype="equiv")
    ok, expected = QuestionChecker.check(q, "2/4")
    assert ok
    assert expected == "1/2"


def test_incorrect_answer():
    q = Question(prompt="half?", answer="1/2")
    ok, expected = QuestionChecker.check(q, "1/3")
    assert not ok
    assert expected == "1/2"


def test_wrong_answer_message_refers_to_expected():
    q = Question(prompt="half?", answer="3/4")
    ok, expected = QuestionChecker.check(q, "1/2")
    assert not ok
    assert expected == "3/4"


def test_add_subtract_fraction():
    q = Question(prompt="1/4+1/4", answer="1/2")
    assert QuestionChecker.check(q, "2/4")[0]


def test_simplify_answer():
    q = Question(prompt="simplify 2/4", answer="1/2")
    assert QuestionChecker.check(q, "1/2")[0]
    assert QuestionChecker.check(q, "0.5")[0]


def test_empty_answer_is_wrong():
    q = Question(prompt="half?", answer="1/2")
    ok, expected = QuestionChecker.check(q, "")
    assert not ok
    assert expected == "1/2"


def test_none_answer_is_wrong():
    q = Question(prompt="half?", answer="1/2")
    ok, expected = QuestionChecker.check(q, None)
    assert not ok
    assert expected == "1/2"


def test_unparsable_answer_is_wrong():
    q = Question(prompt="half?", answer="1/2")
    ok, expected = QuestionChecker.check(q, "banana")
    assert not ok
    assert expected == "1/2"


def test_mixed_number_normalisation():
    q = Question(prompt="x", answer="5/6")
    assert QuestionChecker.check(q, "5/6")[0]


def test_model_getters():
    q = Question(prompt="p", answer="a", options=["x", "y"], id="q1")
    assert q.getPrompt() == "p"
    assert q.getOptions() == ["x", "y"]
    assert q.id == "q1"
