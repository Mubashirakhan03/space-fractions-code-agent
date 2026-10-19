"""Generate fraction questions in code; correct values are computed here.

Every question's correct answer is derived from arithmetic in this module; the
UI/tests never hard-code answers. Wrong choices are distinct and never equal to
(or value-equivalent to) the correct one.
"""
from fractions import Fraction
from random import Random
from typing import List

from question.question import Question, QuestionKind, _frac_str


def _decimal_str(f: Fraction) -> str:
    """Decimal string, rounded to at most 3 significant decimals."""
    val = f.numerator / f.denominator
    # round to 6 decimals and strip trailing zeros / dot (enough precision to
    # distinguish close fractions while remaining human-readable)
    s = f"{val:.6f}".rstrip("0").rstrip(".")
    return s if s else "0"


class FractionGenerator:
    def __init__(self, rng: Random = None):
        self.rng = rng or Random()

    def _random_generator(self, seed=None):
        return Random(seed) if seed is not None else self.rng

    def equivalent_question(self, rng: Random) -> Question:
        a = rng.randint(1, 9)
        b = rng.randint(2, 9)
        base = Fraction(a, b)
        factor = rng.randint(2, 6)
        # multiply numerator AND denominator -> same value, different fraction
        correct = Fraction(a * factor, b * factor)
        wrongs = set()
        while len(wrongs) < 3:
            n = rng.randint(1, 12)
            d = rng.randint(1, 12)
            w = Fraction(n, d)
            if w != base and w not in wrongs:
                wrongs.add(w)
        options = [correct] + list(wrongs)[:3]
        rng.shuffle(options)
        ci = options.index(correct)
        prompt = f"Which fraction equals {_frac_str(base)}?"
        return Question(prompt, [_frac_str(f) for f in options], ci,
                        QuestionKind.EQUIVALENT,
                        explanation=f"{_frac_str(correct)} = {_frac_str(base)}.")

    def simplify_question(self, rng: Random) -> Question:
        n = rng.randint(2, 9)
        d = rng.randint(2, 9)
        factor = rng.randint(2, 6)
        num, den = n * factor, d * factor
        correct = Fraction(n, d)
        wrongs = set()
        while len(wrongs) < 3:
            w = Fraction(rng.randint(1, 12), rng.randint(1, 12))
            if w != correct and w not in wrongs:
                wrongs.add(w)
        options = [correct] + list(wrongs)[:3]
        rng.shuffle(options)
        ci = options.index(correct)
        prompt = f"Reduce {num}/{den} to lowest terms."
        return Question(prompt, [_frac_str(f) for f in options], ci,
                        QuestionKind.SIMPLIFY,
                        explanation=f"{num}/{den} = {_frac_str(correct)}.")

    def decimal_question(self, rng: Random) -> Question:
        a = rng.randint(1, 9)
        b = rng.randint(2, 9)
        correct = Fraction(a, b)
        correct_str = _decimal_str(correct)
        wrongs = set()
        while len(wrongs) < 3:
            w = _decimal_str(Fraction(rng.randint(1, 19), rng.randint(2, 9)))
            if w != correct_str and w not in wrongs:
                wrongs.add(w)
        options = [correct_str] + list(wrongs)[:3]
        rng.shuffle(options)
        ci = options.index(correct_str)
        prompt = f"What is {a}/{b} as a decimal?"
        return Question(prompt, options, ci, QuestionKind.DECIMAL,
                        explanation=f"{a}/{b} = {correct_str}.")

    def larger_question(self, rng: Random) -> Question:
        # ensure the two operands are distinct in value to avoid ambiguity
        a = Fraction(rng.randint(1, 9), rng.randint(2, 9))
        b = Fraction(rng.randint(1, 9), rng.randint(2, 9))
        while b == a:
            b = Fraction(rng.randint(1, 9), rng.randint(2, 9))
        larger = a if a > b else b
        smaller = b if a > b else a
        wrongs = [smaller]
        # add two clearly-wrong distinct values
        while len(wrongs) < 3:
            w = Fraction(rng.randint(1, 9), rng.randint(2, 9))
            if w != larger and w not in wrongs:
                wrongs.append(w)
        options = [larger] + wrongs[:3]
        rng.shuffle(options)
        ci = options.index(larger)
        prompt = f"Which is larger: {_frac_str(a)} or {_frac_str(b)}?"
        return Question(prompt, [_frac_str(f) for f in options], ci,
                        QuestionKind.LARGER,
                        explanation=f"{_frac_str(larger)} > {_frac_str(smaller)}.")

    def generate(self, count: int, seed=None) -> List[Question]:
        rng = self._random_generator(seed)
        kinds = [
            self.equivalent_question,
            self.simplify_question,
            self.decimal_question,
            self.larger_question,
        ]
        out = []
        for i in range(count):
            out.append(rng.choice(kinds)(rng))
        return out
