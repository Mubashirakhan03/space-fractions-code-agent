"""Visual theme for Space Fractions (see DESIGN_DECISIONS.md section 5)."""
from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont

# Palette (hex roles)
BG = "#0B1026"            # deep space background
SURFACE = "#1B2440"       # cards / panels
SURFACE_ALT = "#232F54"   # inputs
PRIMARY = "#4C7DFF"       # buttons
ACCENT = "#FFD166"        # rocket / highlight
ACCENT_2 = "#EF476F"      # fraction stars
SUCCESS = "#06D6A0"       # green
ERROR = "#E63946"         # red
TEXT = "#F4F6FF"          # text on dark
MUTED = "#9AA7D0"         # muted text
HOVER_PRIMARY = "#6B95FF"
HOVER_GREEN = "#3FE8BF"

# Fonts (Tk default family, Segoe UI on Windows)
FAMILY = "Segoe UI"
TITLE_SIZE = 36
CONTENT_SIZE = 26
FEEDBACK_SIZE = 22
BUTTON_SIZE = 18


def font(size: int, weight: str = "normal") -> tkfont.Font:
    return tkfont.Font(family=FAMILY, size=size, weight=weight)


def make_button(parent, text, command, bg=PRIMARY, fg=TEXT, size=BUTTON_SIZE):
    """Create a large, flat button with hover colour."""
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        font=font(size, "bold"),
        activebackground=HOVER_PRIMARY,
        activeforeground=TEXT,
        relief="flat",
        bd=0,
        padx=20,
        pady=8,
        cursor="hand2",
        highlightthickness=0,
    )
    hover = HOVER_PRIMARY if bg == PRIMARY else HOVER_GREEN if bg == SUCCESS else HOVER_PRIMARY

    def on_enter(_e):
        btn.config(bg=hover)

    def on_leave(_e):
        btn.config(bg=bg)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


def make_entry(parent, show=None, width=24):
    return tk.Entry(
        parent,
        font=font(BUTTON_SIZE),
        bg=SURFACE_ALT,
        fg=TEXT,
        insertbackground=TEXT,
        relief="solid",
        bd=1,
        highlightthickness=1,
        highlightbackground=PRIMARY,
        highlightcolor=PRIMARY,
        width=width,
        show=show,
    )


def make_label(parent, text, size=CONTENT_SIZE, fg=TEXT, weight="normal",
               wraplength=None, bg=None, justify="left"):
    return tk.Label(
        parent,
        text=text,
        font=font(size, weight),
        fg=fg,
        bg=bg if bg is not None else parent.cget("bg"),
        wraplength=wraplength,
        justify=justify,
    )
