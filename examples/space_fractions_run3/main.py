"""Space Fractions — entry point (the only module that starts Tk)."""
from __future__ import annotations

import tkinter as tk

from ui.app import create_app


def main():
    root = tk.Tk()
    root.title("Space Fractions")
    root.minsize(1100, 750)
    root.geometry("1200x800")
    try:
        root.state("zoomed")
    except tk.TclError:
        try:
            root.attributes("-zoomed", True)
        except tk.TclError:
            pass
    app = create_app(root)
    app.show("intro")
    root.mainloop()


if __name__ == "__main__":
    main()
