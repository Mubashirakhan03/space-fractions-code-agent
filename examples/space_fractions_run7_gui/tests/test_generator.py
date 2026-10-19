"""Generator tests: recompute expected values independently over many seeds."""
import random

from fractions import Fraction

from game import generator
from question.question import QuestionKind


def _parse(s):
    return Fraction(s)


def test_generated_compare_valid():
    for seed in range(200):
        rng = random.Random(seed)
        q = generator.generate_question(rng)
        if q.kind is not QuestionKind.COMPARE:
            continue
        a = _parse(q.operands["a"])
        b = _parse(q.operands["b"])
        which = q.operands["which"]
        expected = max(a, b) if which == "larger" else min(a, b)
        # assert operands are distinct for an unambiguous item
        assert a != b, f"ambiguous compare at seed {seed}"
        assert _parse(q.correct) == expected
        assert q.correct in q.options
        # all options distinct and none equivalent to correct
        opts = [_parse(o) for o in q.options]
        assert len(set(opts)) == len(opts)
        assert all(o != expected for o in opts if o != expected)


def test_generated_arithmetic_valid():
    for seed in range(200):
        rng = random.Random(seed)
        q = generator.generate_question(rng)
        if q.kind not in (QuestionKind.ADD, QuestionKind.SUBTRACT, QuestionKind.MULTIPLY):
            continue
        a = _parse(q.operands["a"])
        b = _parse(q.operands["b"])
        op = q.operands["op"]
        if op == "+":
            expected = a + b
        elif op == "-":
            expected = a - b
            assert expected >= 0
        else:
            expected = a * b
        assert _parse(q.correct) == expected
        opts = [_parse(o) for o in q.options]
        assert len(set(opts)) == len(opts)
        assert sum(1 for o in opts if o == expected) == 1


def test_generated_simplify_valid():
    for seed in range(200):
        rng = random.Random(seed)
        q = generator.generate_question(rng)
        if q.kind is not QuestionKind.SIMPLIFY:
            continue
        num = q.operands["num"]
        den = q.operands["den"]
        expected = Fraction(num, den)
        assert _parse(q.correct) == expected
        opts = [_parse(o) for o in q.options]
        assert len(set(opts)) == len(opts)


def test_generated_equivalent_valid():
    for seed in range(200):
        rng = random.Random(seed)
        q = generator.generate_question(rng)
        if q.kind is not QuestionKind.EQUIVALENT:
            continue
        base = _parse(q.operands["base"])
        mult = q.operands["multiplier"]
        expected = Fraction(base.numerator * mult, base.denominator * mult)
        assert _parse(q.correct) == expected
        opts = [_parse(o) for o in q.options]
        assert len(set(opts)) == len(opts)
        assert sum(1 for o in opts if o == expected) == 1


def test_generate_many_unique():
    rng = random.Random(42)
    prompts = {q.prompt for q in generator.generate_questions(30, rng)}
    assert len(prompts) > 20
