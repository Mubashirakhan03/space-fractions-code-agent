"""Single source of truth for palette and fonts (UI design brief section 5)."""
import tkinter.font as tkfont

# Palette
BG = "#0B1026"          # deep space navy (background)
SURFACE = "#1A2140"     # panel/card navy
PRIMARY = "#4C5BF0"     # indigo action buttons
PRIMARY_HOVER = "#3A49C8"
ACCENT = "#FFB703"      # star-yellow highlights / correct
SUCCESS = "#2DC653"     # green
ERROR = "#E63946"       # red
TEXT = "#F1FAEE"        # near-white
MUTED = "#9AA7D4"       # muted blue-grey
INPUT_BG = "#232B52"    # input background (differs from surface)
INPUT_BORDER = "#4C5BF0"

# Fonts
FONT_FAMILY = "Segoe UI"


def title_font(size=32):
    return tkfont.Font(family=FONT_FAMILY, size=size, weight="bold")


def body_font(size=24):
    return tkfont.Font(family=FONT_FAMILY, size=size)


def button_font(size=18):
    return tkfont.Font(family=FONT_FAMILY, size=size, weight="bold")
