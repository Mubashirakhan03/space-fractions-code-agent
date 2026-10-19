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
import json, sys, time, tkinter as tk
sys.path.insert(0, ".")
PUMP_SECONDS = 1.2
result = {"checked": [], "problems": []}
try:
    from ui.app import create_app
except Exception as exc:  # ui/app.py exists (checked by the harness) but cannot be imported: a real failure
    msg = f"ui/app.py exists but `from ui.app import create_app` failed: {type(exc).__name__}: {exc}"
    print("UI_PROBE_RESULT " + json.dumps({"checked": [], "problems": [msg]}))
    sys.exit(0)

root = tk.Tk()
callback_errors = []
root.report_callback_exception = lambda et, ev, tb: callback_errors.append(f"{et.__name__}: {ev}")
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


def pump(seconds):
    """Run the event loop for real time so the app's own after() timers (animations, auto-advance) fire."""
    end = time.time() + seconds
    while time.time() < end:
        root.update()
        time.sleep(0.02)


def check(label):
    before = len(callback_errors)
    pump(PUMP_SECONDS)
    for err in callback_errors[before:][:3]:
        result["problems"].append(f"{label}: a Tk callback raised {err} while the screen was running "
                                  "(timers/animations/events must not crash)")
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


def text_of(w):
    try:
        return str(w.cget("text")).strip()
    except tk.TclError:
        return ""


def rect(w):
    x, y = w.winfo_rootx(), w.winfo_rooty()
    return x, y, x + w.winfo_width(), y + w.winfo_height()


def is_ancestor(a, b):
    p = b.master
    while p is not None:
        if p is a:
            return True
        p = p.master
    return False


def check_unfitted(label, screen):
    """A button that is managed (pack/grid/place) inside a visible container but got no room to be shown."""
    for w in walk(screen):
        if (w.winfo_class() in ("Button", "TButton") and not w.winfo_ismapped() and w.winfo_manager()
                and w.master is not None and w.master.winfo_ismapped()):
            result["problems"].append(
                f"{label}: button '{text_of(w)[:25]}' is laid out but not shown — there was no room for it in a "
                f"{root.winfo_width()}x{root.winfo_height()} window. Reduce sizes/padding or let the container grow.")


def check_overlaps(label, screen):
    """A button drawn over a text label on the visible screen (e.g. a fixed-position 'Back' over help text)."""
    widgets = [w for w in walk(screen) if w.winfo_ismapped() and text_of(w)]
    labels = [w for w in widgets if w.winfo_class() in ("Label", "TLabel", "Message")]
    buttons = [w for w in widgets if w.winfo_class() in ("Button", "TButton")]
    for b in buttons:
        bx0, by0, bx1, by1 = rect(b)
        for t in labels:
            if is_ancestor(t, b) or is_ancestor(b, t):
                continue
            tx0, ty0, tx1, ty1 = rect(t)
            iw, ih = min(bx1, tx1) - max(bx0, tx0), min(by1, ty1) - max(by0, ty0)
            if iw <= 0 or ih <= 0:
                continue
            smaller = min((bx1 - bx0) * (by1 - by0), (tx1 - tx0) * (ty1 - ty0)) or 1
            if iw * ih > 0.25 * smaller:
                result["problems"].append(
                    f"{label}: button '{text_of(b)[:25]}' covers the text '{text_of(t)[:40]}' — lay text and buttons "
                    "out with pack/grid (text frame above the button row) instead of fixed overlapping positions.")


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
    if isinstance(screens[name], tk.Misc):
        check_overlaps(f"screen '{name}'", screens[name])
        check_unfitted(f"screen '{name}'", screens[name])

print("UI_PROBE_RESULT " + json.dumps(result), flush=True)  # report before teardown can fail
try:
    for after_id in root.tk.call("after", "info"):
        root.after_cancel(after_id)
    root.destroy()
except tk.TclError:
    pass
'''


def run_ui_probe(runner: PythonRunner, timeout: int = 120) -> tuple[bool, str]:
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
