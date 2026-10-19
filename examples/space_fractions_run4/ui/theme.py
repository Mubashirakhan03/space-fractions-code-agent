"""Central UI design brief: palette, fonts, and small helpers.

Follows DESIGN_DECISIONS.md section 5 (Space Fractions UI design brief).
"""
import tkinter as tk
from tkinter import font as tkfont

# --- palette ---------------------------------------------------------------
BG = "#0B1736"          # deep space background
SURFACE = "#14274E"     # panel / surface
SURFACE_LIGHT = "#1E3566"
PRIMARY = "#FFB400"     # golden yellow (primary buttons)
PRIMARY_HOVER = "#FFCE54"
ACCENT_CYAN = "#23E6FF"
ACCENT_PINK = "#FF6B9D"
ACCENT_GREEN = "#3DDC84"
SUCCESS = "#2ECC71"
ERROR = "#E74C3C"
TEXT = "#FFFFFF"
TEXT_MUTED = "#B8C4E0"

# multiple-choice answer button palette (2x2 grid of 4 colours)
CHOICE_COLORS = [ACCENT_CYAN, ACCENT_PINK, ACCENT_GREEN, PRIMARY]

# --- fonts -----------------------------------------------------------------
_FONTS = {}


def font_family() -> str:
    fams = set(tkfont.families())
    for f in ("Segoe UI", "Verdana", "Helvetica", "Arial"):
        if f in fams:
            return f
    return "TkDefaultFont"


def F(size: int, weight: str = "normal"):
    """Cache and return a tkfont.Font at the given size/weight."""
    key = (size, weight)
    if key not in _FONTS:
        _FONTS[key] = tkfont.Font(family=font_family(), size=size, weight=weight)
    return _FONTS[key]


TITLE_FONT = None   # 36+ pt bold, initialised lazily in theme_bind()
QUESTION_FONT = None
BUTTON_FONT = None
SMALL_FONT = None


def init_fonts():
    global TITLE_FONT, QUESTION_FONT, BUTTON_FONT, SMALL_FONT
    TITLE_FONT = F(40, "bold")
    QUESTION_FONT = F(30, "bold")
    BUTTON_FONT = F(20, "bold")
    SMALL_FONT = F(16)
