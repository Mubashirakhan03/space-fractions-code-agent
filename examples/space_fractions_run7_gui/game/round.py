"""Round construction: random draw + shuffle over seed, admin-added, and generated questions."""
from __future__ import annotations

import random
from typing import List, Optional

from question.question import Question
from game import generator


def build_round(
    pool: List[Question],
    total: int = 10,
    generated_count: int = 5,
    rng: Optional[random.Random] = None,
) -> List[Question]:
    """Build a round of ``total`` questions.

    Draws at random from the whole pool (seed + admin-added) AND code-generated
    questions, then shuffles the combined order so no two rounds are identical.
    """
    rng = rng or random.Random()
    pool_items = list(pool)
    rng.shuffle(pool_items)
    gen_items = generator.generate_questions(generated_count, rng)
    candidates = pool_items + gen_items
    rng.shuffle(candidates)
    selected: List[Question] = []
    for q in candidates:
        if len(selected) >= total:
            break
        selected.append(q)
    return selected


__all__ = ["build_round"]
