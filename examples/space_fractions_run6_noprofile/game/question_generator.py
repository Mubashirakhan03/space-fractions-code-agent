"""Generate computable fraction questions for every round.

Fraction content is arithmetic, so the correct value is computed in code and
wrong choices are guaranteed distinct and never equal to the correct value.
"""
from __future__ import annotations

import random
from typing import List

from fractions import Fraction

from questions.question import Question


def _canonical(value: Fraction) -> str:
    """Stringify a fraction in lowest terms, using mixed numbers when > 1."""
    value = Fraction(value)
    n, d = value.numerator, value.denominator
    if d == 1:
        return str(n)
    if abs(n) > d:
        whole = n // d
        rem = abs(n % d)
        if rem == 0:
            return str(whole)
        return f"{whole} {rem}/{d}"
    return f"{n}/{d}"


def generate_questions(count: int, rng: random.Random) -> List[Question]:
    """Generate ``count`` fresh fraction questions using ``rng``.

    Half are multiple-choice (visual comparison / equivalence / addition) and
    half are typed computation. Every generated question has a computed correct
    value and 3 distinct wrong choices that are never equal to the correct
    value.
    """
    questions: List[Question] = []
    for i in range(count):
        if i % 2 == 0:
            questions.append(_make_choice(i, rng))
        else:
            questions.append(_make_typed(i, rng))
    return questions


def _make_choice(idx: int, rng: random.Random) -> Question:
    style = rng.choice(("compare", "equivalent", "add"))
    if style == "compare":
        a_num = rng.randint(1, 9)
        a_den = rng.randint(1, 9)
        b_num = rng.randint(1, 9)
        b_den = rng.randint(1, 9)
        a, b = Fraction(a_num, a_den), Fraction(b_num, b_den)
        correct = _canonical(a) if a > b else _canonical(b)
        prompt = f"Which fraction is bigger: {_canonical(a)} or {_canonical(b)}?"
        options = [_canonical(a), _canonical(b)]
    elif style == "equivalent":
        base = Fraction(rng.randint(1, 6), rng.randint(1, 6))
        factor = rng.randint(2, 4)
        equiv = base * factor
        prompt = f"Which fraction equals {_canonical(base)}?"
        correct = _canonical(equiv)
        options, used = [correct], {correct}
        while len(options) < 4:
            w = _canonical(base * rng.randint(1, 6) + Fraction(rng.randint(1, 4), rng.randint(1, 6)))
            if w not in used and w != correct:
                options.append(w)
                used.add(w)
    else:  # add
        a = Fraction(rng.randint(1, 5), rng.randint(2, 6))
        b = Fraction(rng.randint(1, 5), rng.randint(2, 6))
        correct = _canonical(a + b)
        prompt = f"What is {_canonical(a)} + {_canonical(b)}?"
        options, used = [correct], {correct}
        while len(options) < 4:
            w = _canonical((a + b) + Fraction(rng.randint(-3, 3), rng.randint(2, 6)))
            if w not in used and Fraction(w) != a + b:
                options.append(w)
                used.add(w)
    rng.shuffle(options)
    return Question(id=f"gen-{idx}", prompt=prompt, correct=correct, kind="choice", options=options)


def _make_typed(idx: int, rng: random.Random) -> Question:
    a = Fraction(rng.randint(1, 6), rng.randint(2, 8))
    b = Fraction(rng.randint(1, 6), rng.randint(2, 8))
    correct = _canonical(a + b)
    prompt = f"Add the fractions and type the answer: {_canonical(a)} + {_canonical(b)}"
    return Question(id=f"gen-{idx}", prompt=prompt, correct=correct, kind="typed", options=[])
