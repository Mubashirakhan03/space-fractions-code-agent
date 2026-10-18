"""Visual constants: light theme, one accent colour, status colours, fonts."""

ACCENT = "#2563EB"
ACCENT_HOVER = "#1D4ED8"
BG = "#F3F4F6"
CARD = "#FFFFFF"
BORDER = "#E5E7EB"
TEXT = "#111827"
MUTED = "#6B7280"
OK = "#16A34A"
ERR = "#DC2626"
WARN = "#D97706"
NEUTRAL_BTN = "#E5E7EB"
NEUTRAL_BTN_HOVER = "#D1D5DB"

# phase status → (background, text colour)
PHASE_COLORS = {
    "pending": ("#E5E7EB", MUTED),
    "running": (ACCENT, "#FFFFFF"),
    "done": (OK, "#FFFFFF"),
    "failed": (ERR, "#FFFFFF"),
    "stopped": (WARN, "#FFFFFF"),
    "skipped": ("#F3F4F6", MUTED),
}
PHASE_CAPTION = {"pending": "pending", "running": "running…", "done": "done", "failed": "failed",
                 "stopped": "stopped", "skipped": "skipped (not needed)"}

# log line tag → colour
LOG_COLORS = {"phase": ACCENT, "tool": "#1E40AF", "ok": OK, "err": ERR, "model": MUTED, "info": TEXT, "warn": WARN}

UI_FONT = "Segoe UI"
MONO_FONT = "Consolas"
