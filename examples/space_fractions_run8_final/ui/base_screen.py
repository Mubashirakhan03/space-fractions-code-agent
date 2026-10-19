"""Shared helpers for screens."""
import tkinter as tk

from ui import theme


def make_button(parent, text, command, **kw):
    font = kw.pop("font", theme.button_font())
    bg = kw.pop("bg", theme.PRIMARY)
    activebackground = kw.pop("activebackground", theme.PRIMARY_HOVER)
    padx = kw.pop("padx", 24)
    pady = kw.pop("pady", 6)
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=theme.TEXT, activebackground=activebackground,
        activeforeground=theme.TEXT, relief="flat", bd=0,
        font=font, cursor="hand2", padx=padx, pady=pady, **kw,
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=activebackground))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def title_label(parent, text, size=32):
    lbl = tk.Label(parent, text=text, bg=theme.BG, fg=theme.TEXT,
                   font=theme.title_font(size))
    return lbl
