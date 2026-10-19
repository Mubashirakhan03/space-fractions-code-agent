"""Space Fractions question domain logic (pure Python, no Tkinter)."""
from .question import Question, QuestionType
from .repository import QuestionRepository

__all__ = ["Question", "QuestionType", "QuestionRepository"]
