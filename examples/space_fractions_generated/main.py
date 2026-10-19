"""Space Fractions — entry point (the only module that starts Tk)."""
import tkinter as tk

from ui.app import create_app


def main():
    root = tk.Tk()
    root.title("Space Fractions")
    root.minsize(1100, 750)
    root.configure(bg="#0B1736")

    try:
        root.state("zoomed")
    except tk.TclError:
        try:
            root.attributes("-zoomed", True)
        except tk.TclError:
            pass

    app = create_app(root)

    def toggle_fullscreen(_event=None):
        current = root.attributes("-fullscreen")
        root.attributes("-fullscreen", not current)

    def leave_fullscreen(_event=None):
        root.attributes("-fullscreen", False)

    root.bind("<F11>", toggle_fullscreen)
    root.bind("<Escape>", leave_fullscreen)

    app.show("intro")
    root.mainloop()


if __name__ == "__main__":
    main()
