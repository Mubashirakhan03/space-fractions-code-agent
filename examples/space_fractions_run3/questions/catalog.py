"""QuestionCatalog — builds a mixed round of questions (all four types)."""
from __future__ import annotations

import random
from typing import List, Optional

from questions.question import Question

ROUND_SIZE = 10


def build_round(
    questions: List[Question],
    size: int = ROUND_SIZE,
    rng: Optional[random.Random] = None,
) -> List[Question]:
    """Return a shuffled round of mixed question types, up to `size`.

    Shuffles across all four types so a round has variety; falls back to all
    questions when fewer than `size` exist.
    """
    rng = rng or random.Random()
    pool = list(questions)
    rng.shuffle(pool)
    return pool[:size]
