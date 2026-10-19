"""Question generator: correct values, distinct wrong choices."""
import random

from fractions import Fraction

from game.question_generator import generate_questions


def _to_fraction(s: str) -> Fraction:
    """Parse a canonical fraction string, incl. mixed numbers like '2 1/2'."""
    s = s.strip()
    if " " in s:
        whole, frac = s.split(" ", 1)
        return int(whole) + Fraction(frac)
    return Fraction(s)


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
            correct_val = _to_fraction(q.correct)
            for o in q.options:
                if o != q.correct:
                    assert _to_fraction(o) != correct_val
        else:
            assert q.check_answer(q.correct)
            assert q.options == []


def test_two_draws_differ():
    a = generate_questions(8, random.Random(1))
    b = generate_questions(8, random.Random(2))
    pa = [q.prompt for q in a]
    pb = [q.prompt for q in b]
    assert pa != pb
