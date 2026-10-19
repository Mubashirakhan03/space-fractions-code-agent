"""Scoring helpers for the Space Fractions game."""
from __future__ import annotations

POINTS_PER_CORRECT = 100


def stars_for(percentage: float) -> int:
    """Return 1-3 stars earned by percentage (>=90:3, >=75:2, >=50:1, else 0)."""
    if percentage >= 90:
        return 3
    if percentage >= 75:
        return 2
    if percentage >= 50:
        return 1
    return 0


def percentage(correct: int, answered: int) -> float:
    """Percentage of correctly answered questions (0 when nothing answered)."""
    if answered <= 0:
        return 0.0
    return round(correct / answered * 100, 1)
