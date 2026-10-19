"""Space Fractions — desktop entry point."""
import tkinter as tk


def main():
    root = tk.Tk()
    from ui.app import create_app
    create_app(root)
    root.mainloop()


if __name__ == "__main__":
    main()
