"""Central theme: colours, fonts, button factory (kid-friendly space look)."""
from __future__ import annotations

import tkinter as tk

# Palette
BG = "#0B1736"           # deep space blue
PANEL = "#12244A"        # panel background
TEXT = "#F4F6FF"         # light text
MUTED = "#8FA0C4"        # muted text
YELLOW = "#FFD54A"
CYAN = "#4AD8FF"
PINK = "#FF6BCD"
GREEN = "#5BF28B"
RED = "#FF5A6E"

ACCENTS = [YELLOW, CYAN, PINK, GREEN]


def font(size: int, weight: str = "normal", family: str = "Segoe UI") -> tuple:
    return (family, size, weight)


def big_button(parent, text, command=None, bg=CYAN, fg=BG, size=20, width=None, pady=14):
    """Large flat button with hover colour."""
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        font=font(size, "bold"),
        relief="flat",
        activebackground=bg,
        activeforeground=fg,
        bd=0,
        highlightthickness=0,
        cursor="hand2",
        pady=pady,
    )
    if width is not None:
        btn.configure(width=width)
    # Hover: lighten by blending toward white a bit
    darker = _blend(bg, "#000000", 0.15)
    btn.bind("<Enter>", lambda e: btn.configure(bg=darker))
    btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
    return btn


def _blend(hex_a, hex_b, t):
    """Blend two #RRGGBB colours, t = amount of b (0..1)."""
    a = hex_a.lstrip("#")
    b = hex_b.lstrip("#")
    ra, ga_, ba = int(a[0:2], 16), int(a[2:4], 16), int(a[4:6], 16)
    rb, gb, bb = int(b[0:2], 16), int(b[2:4], 16), int(b[4:6], 16)
    r = int(ra + (rb - ra) * t)
    g = int(ga_ + (gb - ga_) * t)
    bl = int(ba + (bb - ba) * t)
    return f"#{r:02X}{g:02X}{bl:02X}"
