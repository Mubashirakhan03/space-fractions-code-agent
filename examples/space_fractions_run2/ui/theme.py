"""Central theme: colours and fonts for the Space Fractions UI."""

# Palette (see DESIGN_DECISIONS.md section 5)
BG = "#0B1736"          # deep space background
SURFACE = "#16285A"     # panel surface
SURFACE_ALT = "#1E3A75" # alternate surface
PRIMARY = "#FFD54A"     # yellow
ACCENT_CYAN = "#4DD0E1"
ACCENT_PINK = "#FF6B9D"
ACCENT_GREEN = "#69F0AE"
SUCCESS = "#69F0AE"     # green
ERROR = "#FF5252"       # red
TEXT = "#F5F7FF"
TEXT_MUTED = "#B8C4E0"

PLANET_COLORS = ("#FF6B9D", "#4DD0E1", "#FFD54A", "#69F0AE")
STAR_COLOR = "#FFFFFF"

FONT_FAMILY = "Segoe UI"


def font(size: int, weight: str = "normal") -> tuple:
    return (FONT_FAMILY, size, weight)


TITLE_FONT = font(48, "bold")
SUBTITLE_FONT = font(36, "bold")
QUESTION_FONT = font(30, "bold")
BODY_FONT = font(26)
BUTTON_FONT = font(20, "bold")
INPUT_FONT = font(20)
SMALL_FONT = font(18)
