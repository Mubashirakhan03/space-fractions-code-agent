"""Space Fractions — desktop entry point."""
import tkinter as tk

from ui.app import create_app


def main() -> None:
    root = tk.Tk()
    create_app(root)
    root.mainloop()


if __name__ == "__main__":
    main()
