"""Space Fractions entry point — the only module that starts Tk."""
import tkinter as tk

from ui.app import create_app


def main():
    root = tk.Tk()
    root.title("Space Fractions")
    root.minsize(1100, 750)
    # centre the window
    w, h = 1100, 750
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    x, y = (sw - w) // 2, (sh - h) // 2
    root.geometry(f"{w}x{h}+{max(x, 0)}+{max(y, 0)}")

    create_app(root)

    # open maximized on Windows
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
