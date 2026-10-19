"""Space Fractions — entry point. Only this module starts Tk."""
import tkinter as tk


def main():
    from ui.app import create_app
    root = tk.Tk()
    create_app(root)
    root.mainloop()


if __name__ == "__main__":
    main()
