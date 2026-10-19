"""Space Fractions — entry point (the only module that starts Tk)."""
from __future__ import annotations

import tkinter as tk

from ui.app import create_app


def main() -> None:
    root = tk.Tk()
    create_app(root)
    try:
        root.state("zoomed")
    except tk.TclError:
        try:
            root.attributes("-zoomed", True)
        except tk.TclError:
            pass
    root.mainloop()


if __name__ == "__main__":
    main()
