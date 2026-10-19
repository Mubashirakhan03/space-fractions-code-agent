"""Requirements the harness derives from the spec itself (generic: the words come from the input documents).

- named screens/scenes: features named in the prose (`implied_features`) and the use cases;
- an animated scene, when the spec asks for a movie / animation / animated or opening scene;
- protected roles: administrator-type actors whose screens need an in-window PIN.

The result is listed in the first user message (so the model sees this spec's exact names) and passed to the
UI probe, which fails verification when the animation or the PIN input is missing.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any

ANIMATION_RE = re.compile(
    r"\b(?:[a-z]+\s+)?(?:movie|film|video clip|animation|animated\s+\w+|cinematic|cut-?scene|splash screen|"
    r"intro(?:duction|ductory)?\s+(?:scene|sequence)|opening\s+(?:scene|sequence))\b", re.IGNORECASE)
ADMIN_RE = re.compile(r"\b(admin|administrator|moderator|operator|supervisor)s?\b", re.IGNORECASE)


@dataclass
class SpecRules:
    screens: list[str] = field(default_factory=list)
    use_cases: list[str] = field(default_factory=list)
    animation: list[str] = field(default_factory=list)  # the spec's own phrases, e.g. "introductory movie"
    protected_roles: list[str] = field(default_factory=list)

    def to_probe(self) -> dict[str, Any]:
        return {"animation": self.animation, "protected_roles": self.protected_roles}

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _unique(items: list[str]) -> list[str]:
    seen, out = set(), []
    for item in items:
        key = item.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(item.strip())
    return out


def _prose(spec: dict[str, Any]) -> str:
    doc = spec.get("document") or {}
    parts = [s.get("text", "") for s in doc.get("sections", []) if isinstance(s, dict)]
    parts += [str(x) for x in (spec.get("domain_model") or {}).get("implied_features", [])]
    parts += [json.dumps(r, ensure_ascii=False) for r in spec.get("requirements") or []]
    return "\n".join(parts)


def derive(spec: dict[str, Any]) -> SpecRules:
    dm = spec.get("domain_model") or {}
    screens = _unique([str(x) for x in dm.get("implied_features") or []])
    use_cases = _unique([str(u.get("use_case", "")) for u in dm.get("use_cases") or [] if isinstance(u, dict)])
    animation = _unique([m.group(0) for m in ANIMATION_RE.finditer(_prose(spec))])
    actors = [str(a.get("name", a) if isinstance(a, dict) else a) for a in dm.get("actors") or []]
    actors += [str(u.get("actor", "")) for u in dm.get("use_cases") or [] if isinstance(u, dict)]
    protected = _unique([a for a in actors if ADMIN_RE.search(a)])
    return SpecRules(screens, use_cases, animation, protected)


def checklist(rules: SpecRules) -> str:
    """Markdown block for the first user message; empty when the spec names nothing the harness checks."""
    lines = []
    if rules.screens:
        lines.append("- Screens / scenes / features the spec names (each one implemented, with its own entry in "
                     "App.screens where it is a screen or scene, and reachable in the normal flow): "
                     + "; ".join(rules.screens) + ".")
    if rules.use_cases:
        lines.append("- Use cases (each one doable from the UI): " + "; ".join(rules.use_cases) + ".")
    if rules.animation:
        lines.append(f"- Animated scene REQUIRED — the spec says: {', '.join(repr(a) for a in rules.animation)}. "
                     "Build it as the UI rules describe (Canvas, objects that move, 5-10 s, Skip button, auto-advance, "
                     "test). Verification fails if no screen's canvas items move or the animated screen has no Skip "
                     "button.")
    if rules.protected_roles:
        lines.append(f"- Protected role(s): {', '.join(rules.protected_roles)}. Their screens are reached only through "
                     "an in-window PIN screen (UI rules). Verification fails if no screen has a masked input "
                     "(tk.Entry(show='*')).")
    if not lines:
        return ""
    return "# Harness checklist (derived from this spec; verification checks it)\n" + "\n".join(lines)
