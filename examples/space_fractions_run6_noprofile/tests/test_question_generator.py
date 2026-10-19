"""Question generator: correct values, distinct wrong choices."""
import random

from fractions import Fraction

from game.question_generator import generate_questions


def test_generates_correct_and_distinct_choices():
    rng = random.Random(42)
    qs = generate_questions(40, rng)
    assert len(qs) == 40
    for q in qs:
        if q.kind == "choice":
            assert q.correct in q.options
            # all distinct
            assert len(set(q.options)) == len(q.options)
            # no wrong choice equals the correct value
            correct_val = Fraction(q.correct)
            for o in q.options:
                if o != q.correct:
                    assert Fraction(o) != correct_val
        else:
            assert q.check_answer(q.correct)
            assert q.options == []


def test_two_draws_differ():
    a = generate_questions(8, random.Random(1))
    b = generate_questions(8, random.Random(2))
    pa = [q.prompt for q in a]
    pb = [q.prompt for q in b]
    assert pa != pb
