"""Code-generated fraction questions.

Every generated question carries its operands so tests can RECOMPUTE the expected
answer independently. Wrong choices are distinct and never equal (or equivalent) to
the correct value.
"""
from __future__ import annotations

import random
from fractions import Fraction
from typing import List

from question.question import Question, QuestionKind


def _fmt(f: Fraction) -> str:
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def _make_wrong(correct: Fraction, want: int, rng: random.Random) -> List[str]:
    """Distinct wrong choices, none equivalent to the correct value."""
    out: List[str] = []
    seen = {Fraction(correct)}
    attempts = 0
    while len(out) < want and attempts < 500:
        attempts += 1
        delta = rng.randint(1, 5)
        num = correct.numerator + rng.choice([-delta, delta])
        den = correct.denominator
        if rng.random() < 0.5:
            den += rng.randint(1, 4)
        if den == 0:
            continue
        cand = Fraction(num, den)
        if cand <= 0 or cand in seen:
            continue
        seen.add(cand)
        out.append(_fmt(cand))
    fallback_den = correct.denominator + 1
    while len(out) < want:
        cand = Fraction(correct.numerator + len(out) + 1, fallback_den)
        if cand <= 0 or cand in seen:
            fallback_den += 1
            continue
        seen.add(cand)
        out.append(_fmt(cand))
    return out


def _gen_compare(rng: random.Random) -> Question:
    a_num, a_den = rng.randint(1, 9), rng.randint(2, 12)
    b_num, b_den = rng.randint(1, 9), rng.randint(2, 12)
    a, b = Fraction(a_num, a_den), Fraction(b_num, b_den)
    if a == b:
        b = Fraction(a_num + 1, a_den + rng.randint(1, 4))
    larger = "smaller" if rng.random() < 0.5 else "larger"
    correct_frac = max(a, b) if larger == "larger" else min(a, b)
    prompt = f"Which fraction is {larger}: {_fmt(a)} or {_fmt(b)}?"
    correct = _fmt(correct_frac)
    options = [correct] + [f for f in (_fmt(a), _fmt(b)) if f != correct]
    rng.shuffle(options)
    return Question(
        id=f"gen-cmp-{rng.getrandbits(40)}",
        prompt=prompt,
        correct=correct,
        options=options,
        kind=QuestionKind.COMPARE,
        operands={"a": _fmt(a), "b": _fmt(b), "which": larger},
    )


def _gen_arithmetic(kind: QuestionKind, rng: random.Random) -> Question:
    a = Fraction(rng.randint(1, 6), rng.randint(2, 8))
    b = Fraction(rng.randint(1, 6), rng.randint(2, 8))
    sym = {
        QuestionKind.ADD: "+",
        QuestionKind.SUBTRACT: "-",
        QuestionKind.MULTIPLY: "×",
    }[kind]
    if kind is QuestionKind.ADD:
        correct = a + b
    elif kind is QuestionKind.SUBTRACT:
        if b > a:
            a, b = b, a
        correct = a - b
    else:
        correct = a * b
    prompt = f"What is {_fmt(a)} {sym} {_fmt(b)}?"
    correct_str = _fmt(correct)
    options = [correct_str] + _make_wrong(correct, 3, rng)
    rng.shuffle(options)
    return Question(
        id=f"gen-arith-{rng.getrandbits(40)}",
        prompt=prompt,
        correct=correct_str,
        options=options,
        kind=kind,
        operands={"a": _fmt(a), "b": _fmt(b), "op": sym},
    )


def _gen_simplify(rng: random.Random) -> Question:
    common = rng.randint(2, 6)
    num = rng.randint(1, 6) * common
    den = rng.randint(2, 8) * common
    raw = Fraction(num, den)
    correct = _fmt(raw)
    prompt = f"Simplify {num}/{den}."
    options = [correct] + _make_wrong(raw, 3, rng)
    rng.shuffle(options)
    return Question(
        id=f"gen-simp-{rng.getrandbits(40)}",
        prompt=prompt,
        correct=correct,
        options=options,
        kind=QuestionKind.SIMPLIFY,
        operands={"num": num, "den": den},
    )


def _gen_equivalent(rng: random.Random) -> Question:
    base = Fraction(rng.randint(1, 5), rng.randint(2, 8))
    mult = rng.randint(2, 5)
    correct = Fraction(base.numerator * mult, base.denominator * mult)
    correct_str = _fmt(correct)
    prompt = f"Which fraction is equivalent to {_fmt(base)}?"
    options = [correct_str] + _make_wrong(correct, 3, rng)
    rng.shuffle(options)
    return Question(
        id=f"gen-eq-{rng.getrandbits(40)}",
        prompt=prompt,
        correct=correct_str,
        options=options,
        kind=QuestionKind.EQUIVALENT,
        operands={"base": _fmt(base), "multiplier": mult},
    )


def generate_question(rng: random.Random | None = None) -> Question:
    """Generate one random fraction question of a random kind."""
    rng = rng or random.Random()
    kind = rng.choice(
        [
            QuestionKind.COMPARE,
            QuestionKind.ADD,
            QuestionKind.SUBTRACT,
            QuestionKind.MULTIPLY,
            QuestionKind.SIMPLIFY,
            QuestionKind.EQUIVALENT,
        ]
    )
    if kind is QuestionKind.COMPARE:
        return _gen_compare(rng)
    if kind is QuestionKind.EQUIVALENT:
        return _gen_equivalent(rng)
    if kind is QuestionKind.SIMPLIFY:
        return _gen_simplify(rng)
    return _gen_arithmetic(kind, rng)


def generate_questions(count: int, rng: random.Random | None = None) -> List[Question]:
    rng = rng or random.Random()
    return [generate_question(rng) for _ in range(count)]


__all__ = ["generate_question", "generate_questions"]
