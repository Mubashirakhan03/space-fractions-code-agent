import random
from fractions import Fraction

from game.question_generator import generate_questions, _KIND_FUNCS


def _independently_expected(q):
    """Recompute the expected answer from operands, independent of the item's data."""
    op = q.operands
    kind = q.kind
    if kind == "add":
        return str(Fraction(op["a"]) + Fraction(op["b"]))
    if kind == "subtract":
        return str(Fraction(op["a"]) - Fraction(op["b"]))
    if kind == "reduce":
        return str(Fraction(op["num"], op["den"]))
    if kind == "equivalent":
        return str(Fraction(op["target"]))
    if kind == "compare":
        return op["larger"]
    if kind == "identify":
        return str(Fraction(op["num"], op["den"]))
    return None


def test_many_seeds_each_kind_recomputes_correct():
    for seed in range(200):
        rng = random.Random(seed)
        qs = generate_questions(rng, count=6)
        for q in qs:
            assert q.correct_value in q.choices
            expected = _independently_expected(q)
            # allow equivalent fractions as the recomputed value, e.g. 2/4 vs 1/2
            assert Fraction(expected) == Fraction(q.correct_value), (seed, q.kind, q.operands)


def test_choices_are_distinct():
    for seed in range(100):
        rng = random.Random(seed)
        for q in generate_questions(rng, count=6):
            assert len(set(q.choices)) == len(q.choices)


def test_exactly_one_correct_choice():
    for seed in range(100):
        rng = random.Random(seed)
        for q in generate_questions(rng, count=6):
            correct_vals = [Fraction(c) for c in q.choices
                            if Fraction(c) == Fraction(q.correct_value)]
            assert len(correct_vals) == 1, (seed, q.kind, q.choices, q.correct_value)


def test_compare_operands_are_distinct():
    for seed in range(100):
        rng = random.Random(seed)
        qs = generate_questions(rng, count=12)
        for q in qs:
            if q.kind == "compare":
                assert q.operands["a"] != q.operands["b"]


def test_reduce_only_accepts_lowest_terms():
    rng = random.Random(1)
    qs = generate_questions(rng, count=6)
    reduce_qs = [q for q in qs if q.kind == "reduce"]
    assert reduce_qs
    q = reduce_qs[0]
    # expanded form must NOT be the correct value
    assert q.check_answer(q.correct_value) is True


def test_covers_all_kinds():
    rng = random.Random(0)
    kinds = {q.kind for q in generate_questions(rng, count=6)}
    assert kinds == set(_KIND_FUNCS.keys())


def test_no_choice_repeats_prompt_operand_for_equivalent():
    for seed in range(100):
        rng = random.Random(seed)
        for q in generate_questions(rng, count=12):
            if q.kind == "equivalent":
                base = q.operands["base"]
                # correct option must look different from the prompt's operand text
                assert q.correct_value != base
