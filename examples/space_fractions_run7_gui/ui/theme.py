"""Centralised theme: palette, fonts, colours (UI design brief section 5)."""
from __future__ import annotations

import tkinter as tk

# --- palette ---
BACKGROUND = "#0B1026"
SURFACE = "#1B2144"
PRIMARY = "#4A90E2"
ACCENT = "#FFD166"
SECONDARY = "#9B5DE5"
SUCCESS = "#43D17C"
ERROR = "#FF5D73"
TEXT = "#F4F6FF"
MUTED = "#A9B4D6"
INPUT_BG = "#232A54"
HOVER = "#5DA1EE"

# --- fonts (Segoe UI, large readable) ---
TITLE_FONT = ("Segoe UI", 40, "bold")
SUBTITLE_FONT = ("Segoe UI", 26, "bold")
CONTENT_FONT = ("Segoe UI", 26)
BUTTON_FONT = ("Segoe UI", 20, "bold")
INPUT_FONT = ("Segoe UI", 20)
FEEDBACK_FONT = ("Segoe UI", 24, "bold")
SMALL_FONT = ("Segoe UI", 16)
LABEL_FONT = ("Segoe UI", 18)


def style_button(btn: tk.Widget) -> None:
    """Apply flat, large, high-contrast button styling with hover colour."""
    btn.configure(
        bg=PRIMARY,
        fg=TEXT,
        font=BUTTON_FONT,
        relief="flat",
        activebackground=HOVER,
        activeforeground=TEXT,
        padx=18,
        pady=7,
        bd=0,
        cursor="hand2",
    )
    btn.bind("<Enter>", lambda e: btn.configure(bg=HOVER))
    btn.bind("<Leave>", lambda e: btn.configure(bg=PRIMARY))


def style_entry(entry: tk.Widget) -> None:
    entry.configure(
        bg=INPUT_BG,
        fg=TEXT,
        insertbackground=TEXT,
        font=INPUT_FONT,
        relief="solid",
        bd=2,
        highlightthickness=1,
        highlightbackground=PRIMARY,
        highlightcolor=PRIMARY,
    )


__all__ = [
    "BACKGROUND", "SURFACE", "PRIMARY", "ACCENT", "SECONDARY", "SUCCESS",
    "ERROR", "TEXT", "MUTED", "INPUT_BG", "HOVER",
    "TITLE_FONT", "SUBTITLE_FONT", "CONTENT_FONT", "BUTTON_FONT", "INPUT_FONT",
    "FEEDBACK_FONT", "SMALL_FONT", "LABEL_FONT",
    "style_button", "style_entry",
]
