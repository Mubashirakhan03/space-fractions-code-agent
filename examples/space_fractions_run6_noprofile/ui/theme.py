"""Central palette and fonts for the Space Fractions UI."""
import tkinter.font as tkfont

# Palette (hex) -------------------------------------------------------------
BG = "#0B1026"          # deep space background
SURFACE = "#1C2340"     # raised panels / cards
PRIMARY = "#4C6EF5"     # electric blue (primary buttons)
ACCENT = "#FFD43B"      # warm gold (titles, stars, highlights)
VIOLET = "#9775FA"      # secondary accent
SUCCESS = "#40C057"     # green (correct)
ERROR = "#FA5252"       # red (wrong)
TEXT = "#F1F3F5"        # near-white text
TEXT_MUTED = "#ADB5BD"  # secondary text

# Font families and sizes ---------------------------------------------------
FAMILY = "Segoe UI"


def font(size: int, weight: str = "normal") -> tuple:
    """Return a tkinter font tuple (family, size, weight)."""
    return (FAMILY, size, weight)


TITLE = font(36, "bold")
HEADING = font(30, "bold")
QUESTION = font(26, "bold")
BODY = font(20)
BUTTON = font(20, "bold")
SMALL = font(16)
INPUT = font(18)


def available(family: str = FAMILY) -> str:
    """Return ``family`` if it exists on this system, else the Tk default."""
    try:
        names = set(tkfont.families())
    except Exception:
        return "TkDefaultFont"
    return family if family in names else "TkDefaultFont"
