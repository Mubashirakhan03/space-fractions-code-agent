"""Central palette and fonts for the Space Fractions UI (design brief §5)."""
from __future__ import annotations

import tkinter.font as tkfont

# Palette
BG = "#0B1736"            # deep space navy (canvas background)
SURFACE = "#16264A"       # panels
SURFACE_ALT = "#1D2F5C"   # lighter panels / hover surface
PRIMARY = "#FFD166"       # warm yellow star
ACCENT = "#36E0D0"        # cyan
ACCENT_2 = "#FF6EC7"      # pink
ACCENT_3 = "#6EEB7E"      # green
SUCCESS = "#6EEB7E"
ERROR = "#FF6B6B"
TEXT = "#F2F6FF"
TEXT_MUTED = "#9FB0D8"
STAR_FILL = "#FFD166"
STAR_EMPTY = "#3A4A72"

# Answer button colours (alternating so the 2x2 grid is colourful).
ANSWER_COLORS = [ACCENT, ACCENT_2, ACCENT_3, PRIMARY]


def font_family(root) -> str:
    """Pick a large, readable font family (Segoe UI on Windows)."""
    fams = set(tkfont.families(root))
    for name in ("Segoe UI", "Verdana", "Tahoma", "Arial"):
        if name in fams:
            return name
    return "Helvetica"


class Theme:
    """Holds a shared font family and sized font helpers."""

    def __init__(self, root) -> None:
        self.family = font_family(root)

    def title(self):
        return (self.family, 40, "bold")

    def heading(self):
        return (self.family, 30, "bold")

    def question(self):
        return (self.family, 30)

    def body(self):
        return (self.family, 20)

    def label(self):
        return (self.family, 18)

    def button(self):
        return (self.family, 20, "bold")

    def small(self):
        return (self.family, 16)
