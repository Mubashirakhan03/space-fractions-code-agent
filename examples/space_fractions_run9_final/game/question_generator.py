"""Generator for computable fraction questions.

The correct value is always computed in code; wrong choices are distinct and
never equal (or equivalent) to the correct value. Items are unambiguous (no two
equal operands in a "which is larger" comparison).
"""
from __future__ import annotations

import random
from fractions import Fraction
from typing import List

from question.question import GeneratedQuestion

_LETTERS = "ABCD"


def _fmt(f: Fraction) -> str:
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def _random_fraction(rng: random.Random, max_den: int = 9) -> Fraction:
    den = rng.randint(2, max_den)
    num = rng.randint(1, den)
    return Fraction(num, den)


def _wrong_choices(correct: Fraction, n: int, rng: random.Random,
                   max_den: int = 9) -> List[str]:
    choices = set()
    guard = 0
    while len(choices) < n and guard < 200:
        f = _random_fraction(rng, max_den)
        if f != correct:
            choices.add(_fmt(f))
        guard += 1
    return list(choices)


def _mk(kind: str, prompt: str, correct: Fraction, rng: random.Random,
        operands: dict, n_wrong: int = 3) -> GeneratedQuestion:
    wrong = _wrong_choices(correct, n_wrong, rng)
    choices = [_fmt(correct)] + wrong
    rng.shuffle(choices)
    return GeneratedQuestion(
        id=f"gen-{kind}-{rng.getrandbits(24):06x}",
        prompt=prompt,
        choices=choices,
        correct_value=_fmt(correct),
        kind=kind,
        operands=operands,
    )


def _identify_question(rng: random.Random) -> GeneratedQuestion:
    num = rng.randint(1, 5)
    den = rng.randint(2, 9)
    frac = Fraction(num, den)
    return _mk(
        "identify",
        f"Which fraction of the circle is shaded? Shown as {_fmt(frac)}",
        frac, rng,
        {"num": num, "den": den},
    )


def _compare_question(rng: random.Random) -> GeneratedQuestion:
    a = _random_fraction(rng)
    b = _random_fraction(rng)
    while b == a:
        b = _random_fraction(rng)
    larger = a if a > b else b
    return _mk(
        "compare",
        f"Which fraction is larger: {_fmt(a)} or {_fmt(b)}?",
        larger, rng,
        {"a": _fmt(a), "b": _fmt(b), "larger": _fmt(larger)},
    )


def _add_question(rng: random.Random) -> GeneratedQuestion:
    a = _random_fraction(rng, 6)
    b = _random_fraction(rng, 6)
    total = a + b
    return _mk(
        "add",
        f"What is {_fmt(a)} + {_fmt(b)}?",
        total, rng,
        {"a": _fmt(a), "b": _fmt(b)},
    )


def _subtract_question(rng: random.Random) -> GeneratedQuestion:
    a = _random_fraction(rng, 6)
    b = _random_fraction(rng, 6)
    if b > a:
        a, b = b, a
    diff = a - b
    return _mk(
        "subtract",
        f"What is {_fmt(a)} - {_fmt(b)}?",
        diff, rng,
        {"a": _fmt(a), "b": _fmt(b)},
    )


def _reduce_question(rng: random.Random) -> GeneratedQuestion:
    base = _random_fraction(rng, 6)
    factor = rng.randint(2, 4)
    num = base.numerator * factor
    den = base.denominator * factor
    # Display the expanded (non-reduced) form so there is something to reduce.
    expanded_str = f"{num}/{den}"
    reduced = base
    q = _mk(
        "reduce",
        f"Reduce {expanded_str} to lowest terms.",
        reduced, rng,
        {"num": num, "den": den, "reduced": _fmt(reduced)},
    )
    return q


def _equivalent_question(rng: random.Random) -> GeneratedQuestion:
    base = _random_fraction(rng, 5)
    factor = rng.randint(2, 4)
    num = base.numerator * factor
    den = base.denominator * factor
    # Answer is the expanded form of `base`, which looks different from `base`.
    target_str = f"{num}/{den}"
    q = _mk(
        "equivalent",
        f"Which fraction is equivalent to {_fmt(base)}?",
        Fraction(num, den), rng,
        {"base": _fmt(base), "target": target_str},
    )
    q.correct_value = target_str
    # rebuild choices so the displayed correct option is the expanded form
    wrong = _wrong_choices(Fraction(num, den), 3, rng)
    wrong = [w for w in wrong if Fraction(w) != Fraction(num, den)]
    choices = [target_str] + wrong
    rng.shuffle(choices)
    q.choices = choices
    return q


_KIND_FUNCS = {
    "identify": _identify_question,
    "compare": _compare_question,
    "add": _add_question,
    "subtract": _subtract_question,
    "reduce": _reduce_question,
    "equivalent": _equivalent_question,
}


def generate_questions(rng: random.Random, count: int = 10) -> List[GeneratedQuestion]:
    """Generate `count` computable questions cycling through all kinds."""
    result: List[GeneratedQuestion] = []
    kinds = list(_KIND_FUNCS.keys())
    rng.shuffle(kinds)
    for i in range(count):
        kind = kinds[i % len(kinds)]
        result.append(_KIND_FUNCS[kind](rng))
    return result
