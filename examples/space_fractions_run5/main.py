"""Entry point for Space Fractions. The only module that starts Tk."""
from __future__ import annotations

import tkinter as tk

from ui.app import create_app


def main() -> None:
    root = tk.Tk()
    root.title("Space Fractions")
    app = create_app(root)
    app.show("intro")
    root.mainloop()


if __name__ == "__main__":
    main()
