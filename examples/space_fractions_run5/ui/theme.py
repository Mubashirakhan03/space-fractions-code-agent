"""Central theme: palette and fonts for the Space Fractions UI."""
from __future__ import annotations

import tkinter.font as tkfont

# ---- palette ---------------------------------------------------------------
SPACE_BG = "#0B1736"        # deep space background
PANEL = "#14265A"           # panel / surface
PRIMARY = "#2C7BD6"         # primary buttons
ACCENT_YELLOW = "#FFD166"
ACCENT_CYAN = "#4ECDC4"
ACCENT_PINK = "#FF6B9D"
ACCENT_GREEN = "#3DDC84"
SUCCESS = "#3DDC84"
ERROR = "#FF5A5F"
TEXT = "#FFFFFF"
MUTED_TEXT = "#AEC6E8"

HOVER = "#3E8BE0"           # primary button hover


# ---- fonts -----------------------------------------------------------------
def _font(family: str, size: int, weight: str = "normal"):
    return (family, size, weight)


TITLE_FONT = _font("Verdana", 40, "bold")
SUBTITLE_FONT = _font("Verdana", 26, "bold")
QUESTION_FONT = _font("Verdana", 30, "bold")
BODY_FONT = _font("Verdana", 20)
BUTTON_FONT = _font("Verdana", 22, "bold")
INPUT_FONT = _font("Verdana", 22)
SMALL_FONT = _font("Verdana", 16)
FEEDBACK_FONT = _font("Verdana", 26, "bold")
