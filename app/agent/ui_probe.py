"""Harness-side UI layout probe (part of Verify).

Tests written by the model can pass while the window still looks broken — e.g. a Canvas background
drawn before the window is shown (winfo_width() is 1 until then), so every star lands in the
top-left corner. The probe opens the generated app for real (normal 1280x800 window, ~1-2 s), shows
every screen via the contract `create_app(root)` → `app.screens` / `app.show(name)`, and reports
widgets outside the window, canvases whose items are squeezed into a corner or drawn off-canvas,
and screens that raise when shown. It is generic: it knows nothing about the specific app.
"""

from __future__ import annotations

import json

from app.tools.runner import PythonRunner

PROBE_REL = "agent_run/ui_probe.py"

PROBE_SOURCE = r'''
import json, sys, tkinter as tk
sys.path.insert(0, ".")
result = {"checked": [], "problems": []}
try:
    from ui.app import create_app
except Exception as exc:
    print("UI_PROBE_RESULT " + json.dumps({"skipped": f"ui.app.create_app not importable: {exc}"}))
    sys.exit(0)

root = tk.Tk()
try:
    app = create_app(root)
except Exception as exc:
    msg = f"create_app(root) raised {type(exc).__name__}: {exc}"
    print("UI_PROBE_RESULT " + json.dumps({"checked": [], "problems": [msg]}))
    sys.exit(0)
for attempt in (lambda: root.state("normal"), lambda: root.attributes("-fullscreen", False)):
    try:
        attempt()
    except tk.TclError:
        pass
root.geometry("1280x800+40+40")
root.update()


def walk(widget):
    yield widget
    for child in widget.winfo_children():
        yield from walk(child)


def check(label):
    for _ in range(3):
        root.update()
    width, height = root.winfo_width(), root.winfo_height()
    ox, oy = root.winfo_rootx(), root.winfo_rooty()
    visible = 0
    for w in walk(root):
        cls = w.winfo_class()
        if not w.winfo_ismapped():
            continue
        if cls in ("Label", "Button", "Entry", "TLabel", "TButton", "TEntry"):
            cx = w.winfo_rootx() - ox + w.winfo_width() / 2
            cy = w.winfo_rooty() - oy + w.winfo_height() / 2
            if 0 <= cx <= width and 0 <= cy <= height:
                visible += 1
            else:
                try:
                    text = str(w.cget("text"))[:30]
                except tk.TclError:
                    text = ""
                result["problems"].append(f"{label}: {cls} '{text}' is outside the visible window "
                                          f"(centre at {int(cx)},{int(cy)} in a {width}x{height} window)")
        elif cls == "Canvas":
            items = w.find_all()
            cw, ch = w.winfo_width(), w.winfo_height()
            if len(items) < 10 or cw < 50:
                continue
            boxes = [w.bbox(i) for i in items]
            boxes = [b for b in boxes if b]
            inside = sum(1 for b in boxes if b[2] > 0 and b[3] > 0 and b[0] < cw and b[1] < ch)
            cornered = sum(1 for b in boxes if b[2] <= 6 or b[3] <= 6)  # collapsed to a strip: w or h was 1
            if cornered >= 10:
                result["problems"].append(
                    f"{label}: {cornered} of {len(items)} canvas items are squeezed into the top-left edge — they "
                    "were drawn before the canvas had its real size (winfo_width() returns 1 until the window "
                    "is shown). Draw/redraw canvas content in a <Configure> handler using event.width/height.")
            elif inside < 0.5 * len(boxes):
                result["problems"].append(
                    f"{label}: only {inside} of {len(boxes)} canvas items are inside the visible {cw}x{ch} canvas; "
                    "compute positions from the real size in a <Configure> handler.")
    if visible == 0:
        result["problems"].append(f"{label}: no labels, buttons or inputs are visible")
    result["checked"].append(label)


check("startup view")
screens = getattr(app, "screens", None) or getattr(app, "_screens", None) or {}
for name in list(screens) if isinstance(screens, dict) else []:
    try:
        app.show(name)
    except Exception as exc:
        result["problems"].append(f"screen '{name}': app.show() raised {type(exc).__name__}: {exc} "
                                  "(screens must render safely even when shown directly)")
        continue
    check(f"screen '{name}'")

print("UI_PROBE_RESULT " + json.dumps(result), flush=True)  # report before teardown can fail
try:
    for after_id in root.tk.call("after", "info"):
        root.after_cancel(after_id)
    root.destroy()
except tk.TclError:
    pass
'''


def run_ui_probe(runner: PythonRunner, timeout: int = 60) -> tuple[bool, str]:
    """Write and run the probe with the bundled interpreter. Returns (ok, report text)."""
    target = runner.root / PROBE_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(PROBE_SOURCE, encoding="utf-8")
    if not (runner.root / "ui" / "app.py").is_file():
        return True, "UI PROBE SKIPPED: ui/app.py not found (create_app contract not used)."
    ok, out = runner.run_script(PROBE_REL, timeout=timeout)
    line = next((ln for ln in reversed(out.splitlines()) if ln.startswith("UI_PROBE_RESULT ")), None)
    if line is None:
        return False, "UI PROBE FAILED to run (the app crashed while opening its screens):\n" + out[-3000:]
    data = json.loads(line[len("UI_PROBE_RESULT "):])
    if "skipped" in data:
        return True, f"UI PROBE SKIPPED: {data['skipped']}"
    problems = data.get("problems", [])
    checked = ", ".join(data.get("checked", []))
    if problems:
        return False, (f"UI LAYOUT PROBLEMS ({len(problems)}) found by opening the real window "
                       f"(checked: {checked}):\n- " + "\n- ".join(problems[:25]))
    return True, f"UI PROBE OK: {checked}"
