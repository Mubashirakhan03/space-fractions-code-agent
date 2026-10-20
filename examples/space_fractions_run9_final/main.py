"""Space Fractions — a desktop fraction-practice game.

Entry point: `python main.py`. The only module that starts Tk.
"""
from __future__ import annotations

import tkinter as tk


def main() -> None:
    from ui.app import create_app
    root = tk.Tk()
    app = create_app(root)
    root.mainloop()


if __name__ == "__main__":
    main()
