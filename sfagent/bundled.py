"""Standard-library modules guaranteed to be inside the frozen exe.

PyInstaller only bundles what our own code imports, but the *generated* game and its tests run on
the exe's interpreter too. This single list is used by the PyInstaller spec (hidden imports) and
by the system prompt (so the model only uses modules that will exist on the target PC).
"""

BUNDLED_STDLIB = [
    "tkinter", "tkinter.ttk", "tkinter.messagebox", "tkinter.simpledialog", "tkinter.filedialog",
    "tkinter.font", "tkinter.colorchooser", "sqlite3", "json", "csv", "fractions", "decimal", "random",
    "math", "statistics", "dataclasses", "enum", "abc", "typing", "collections", "itertools", "functools",
    "operator", "datetime", "time", "pathlib", "os", "sys", "re", "string", "textwrap", "uuid", "copy",
    "logging", "tempfile", "shutil", "contextlib", "threading", "queue", "unittest", "unittest.mock",
    "io", "traceback", "heapq", "bisect", "pprint", "argparse", "configparser", "hashlib", "importlib",
]
TEST_PACKAGES = ["pytest"]
