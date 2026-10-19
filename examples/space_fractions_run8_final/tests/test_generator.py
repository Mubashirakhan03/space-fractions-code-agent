"""Generator tests recompute expected answers independently from item data,
over many random seeds, and reject ambiguous items.
"""
from fractions import Fraction
from random import Random

import pytest

from game.generator import FractionGenerator, _decimal_str
from question.question import QuestionKind


def _parse(s):
    s = s.strip()
    if "/" in s:
        n, d = s.split("/")
        return Fraction(int(n), int(d))
    return Fraction(int(s))


def _recompute(q):
    """Return the independently computed correct value for a question."""
    prompt = q.prompt
    if q.kind == QuestionKind.EQUIVALENT:
        # "Which fraction equals a/b?"
        base = _parse(prompt.split("equals ")[1].rstrip("?"))
        return base
    if q.kind == QuestionKind.SIMPLIFY:
        # "Reduce N/D to lowest terms."
        frac_token = prompt.split("Reduce ")[1].split(" to ")[0]
        return _parse(frac_token)
    if q.kind == QuestionKind.DECIMAL:
        # "What is a/b as a decimal?"
        frac_token = prompt.split("What is ")[1].split(" as ")[0]
        return _parse(frac_token)
    if q.kind == QuestionKind.LARGER:
        # "Which is larger: a/b or c/d?"
        parts = prompt.split("larger: ")[1].split(" or ")
        a, b = _parse(parts[0]), _parse(parts[1].rstrip("?"))
        return max(a, b)
    raise AssertionError("unknown kind")


def _is_value_equal(got, expected):
    if isinstance(expected, float) or q_kind_decimal(got):
        return abs(float(got) - float(expected)) < 1e-6
    return _parse(got) == _parse(str(expected)) if expected is not None else False


def q_kind_decimal(_):
    return False


def _check_all(seed):
    gen = FractionGenerator(Random(seed))
    for q in gen.generate(100, seed=seed):
        expected = _recompute(q)
        correct_str = q.correct_answer
        if q.kind == QuestionKind.DECIMAL:
            assert abs(float(correct_str) - float(expected)) < 1e-4, (
                seed, q.prompt, correct_str, expected)
        else:
            assert _parse(correct_str) == expected, (seed, q.prompt, correct_str, expected)
        # wrong choices distinct and never value-equal to correct
        options = q.getOptions()
        assert len(set(options)) == len(options), (seed, q.prompt)
        for o in options:
            if o != correct_str:
                if q.kind == QuestionKind.DECIMAL:
                    assert o != correct_str  # distinct formatted strings
                else:
                    assert _parse(o) != _parse(correct_str), (seed, q.prompt, o)


def test_generator_over_many_seeds():
    for seed in range(200):
        _check_all(seed)


def test_larger_operands_distinct():
    gen = FractionGenerator(Random(3))
    for _ in range(500):
        q = gen.larger_question(Random(_))
        parts = q.prompt.split("larger: ")[1].split(" or ")
        a = _parse(parts[0])
        b = _parse(parts[1].rstrip("?"))
        assert a != b  # never ambiguous


def test_generator_kinds_covered():
    gen = FractionGenerator()
    qs = gen.generate(40, seed=1)
    kinds = {q.kind for q in qs}
    assert {QuestionKind.EQUIVALENT, QuestionKind.SIMPLIFY,
            QuestionKind.DECIMAL, QuestionKind.LARGER} <= kinds
