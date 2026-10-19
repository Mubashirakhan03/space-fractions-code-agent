"""Tolerant PlantUML parser for `Architecture_View.md`.

Every `@startuml … @enduml` block becomes a diagram dict: name, view (Scenario/Logic/Process/
Development/Physical), type, elements and relations. Non-standard syntax found in the input
(Mermaid `->>` arrows, `participant` inside an object diagram, …) is normalised and reported in
`warnings` instead of failing.
"""

from __future__ import annotations

import re
from typing import Any

VIEW_RE = re.compile(r"^##\s+(\w+?)View\s*$")
TITLE_RE = re.compile(r"^\s*\d+\.\s+(\w+)\s+[—-]\s+(.+?)\s*$")
START_RE = re.compile(r"^@startuml\s*(\S*)")

NAME = r"(?:\[\*\]|\([^)]+\)|\"[^\"]+\"|[\w.]+)"
RELATION_RE = re.compile(
    rf"^(?P<src>{NAME})\s*(?P<arrow>[<>*o|.\-]*[-.][<>*o|.\-]*)\s*(?P<dst>{NAME})\s*(?::\s*(?P<label>.*))?$"
)

ARROW_KINDS = {
    "--": "association", "..": "association",
    "-->": "directed", "->": "message", "->>": "message",
    "--*": "composition", "*--": "composition", "o--": "aggregation", "--o": "aggregation",
    "<|--": "inheritance", "--|>": "inheritance", "..>": "dependency", "<..": "dependency",
}
ELEMENT_KEYWORDS = ["actor", "participant", "object", "state", "node", "artifact", "component",
                    "database", "class", "package", "rectangle", "interface", "usecase"]
EXPECTED_TYPES = {  # diagram type → element kinds that belong in it
    "Object": {"object"},
    "Sequence": {"participant", "actor"},
    "Collaboration": {"participant", "actor", "object"},
}


def _clean(name: str) -> str:
    return name.strip().strip("()").strip('"').strip()


def parse_views(text: str) -> dict[str, Any]:
    """Parse all diagrams in the markdown file."""
    diagrams: list[dict[str, Any]] = []
    warnings: list[str] = []
    view, dtype, title = None, None, None
    buf: list[str] | None = None
    for line in text.splitlines():
        s = line.strip()
        if buf is not None:
            if s.startswith("@enduml"):
                d = parse_diagram(buf, view=view, dtype=dtype, title=title)
                diagrams.append(d)
                warnings += [f"{d['name']}: {w}" for w in d["warnings"]]
                buf = None
            else:
                buf.append(line)
            continue
        if m := VIEW_RE.match(s):
            view = m.group(1)
        elif m := TITLE_RE.match(s):
            dtype, title = m.group(1), m.group(2)
        elif START_RE.match(s):
            buf = [s]
    if buf is not None:
        warnings.append("Unterminated @startuml block at end of file.")
    return {"diagrams": diagrams, "warnings": warnings}


def parse_diagram(lines: list[str], *, view: str | None, dtype: str | None, title: str | None) -> dict[str, Any]:
    name = START_RE.match(lines[0]).group(1) or "Unnamed"
    d: dict[str, Any] = {"name": name, "view": view, "type": dtype or "Unknown", "title": title,
                         "elements": [], "relations": [], "notes": [], "activity": [], "warnings": []}
    by_id: dict[str, dict[str, Any]] = {}
    containers: list[dict[str, Any]] = []
    current_class: dict[str, Any] | None = None
    mermaid_arrows = 0

    def element(kind: str, ident: str, label: str | None = None) -> dict[str, Any]:
        ident = _clean(ident)
        parent = containers[-1]["id"] if containers else None
        existing = by_id.get(ident)
        # Same name may be reused for a different kind (e.g. `package Game { class Game }`).
        if existing and (kind == "implicit" or (existing["kind"] == kind and existing.get("parent") == parent)):
            return existing
        el: dict[str, Any] = {"id": ident, "kind": kind, "label": _clean(label) if label else ident}
        if parent:
            el["parent"] = parent
        if kind == "class":
            el.update(attributes=[], methods=[])
        by_id.setdefault(ident, el)
        d["elements"].append(el)
        return el

    for raw in lines[1:]:
        s = raw.strip()
        if not s or s.startswith("'") or s in {"left to right direction", "top to bottom direction"}:
            continue
        if current_class is not None:
            if s == "}":
                current_class = None
            else:
                _class_member(current_class, s)
            continue
        if s == "}":
            if containers:
                containers.pop()
            continue
        if _activity_line(d, s):
            continue
        if m := re.match(r"^note\s+(?:left|right|top|bottom)\s+of\s+(\w+)\s*:\s*(.+)$", s):
            d["notes"].append({"target": m.group(1), "text": m.group(2)})
            continue
        if m := re.match(r'^usecase\s+"([^"]+)"\s+as\s+(\(?\w+\)?)', s):
            element("usecase", m.group(2), m.group(1))
            continue
        if m := re.match(rf"^({'|'.join(ELEMENT_KEYWORDS)})\s+(.+?)\s*(\{{)?$", s):
            kind, rest, brace = m.group(1), m.group(2), m.group(3)
            alias = re.match(r'^(?:"([^"]+)"\s+as\s+(\w+)|(\w+)\s+as\s+"([^"]+)"|(\S+))$', rest)
            ident, label = rest, None
            if alias:
                ident = alias.group(2) or alias.group(3) or alias.group(5)
                label = alias.group(1) or alias.group(4)
            el = element(kind, ident, label)
            if brace and kind == "class":
                current_class = el
            elif brace:
                containers.append(el)
            continue
        if m := RELATION_RE.match(s):
            arrow = m.group("arrow")
            if arrow == "->>":
                mermaid_arrows += 1
            src, dst = _clean(m.group("src")), _clean(m.group("dst"))
            for end in (src, dst):
                if end != "[*]" and end not in by_id:
                    element("implicit", end)
            d["relations"].append({"from": src, "to": dst, "arrow": arrow,
                                   "kind": ARROW_KINDS.get(arrow, "other"),
                                   "label": (m.group("label") or "").strip() or None})
            continue
        d["warnings"].append(f"Unrecognised line kept as raw text: {s}")
        d.setdefault("raw", []).append(s)

    if mermaid_arrows:
        d["warnings"].append(f"{mermaid_arrows} Mermaid-style '->>' arrow(s) are not PlantUML; normalised to '->'.")
    _check_types(d)
    return d


def _class_member(cls: dict[str, Any], s: str) -> None:
    vis = {"+": "public", "-": "private", "#": "protected", "~": "package"}
    m = re.match(r"^([+\-#~])?\s*(\w+)\s*\((.*?)\)\s*(?::\s*(.+))?$", s)
    if m:
        params = [p.strip() for p in m.group(3).split(",") if p.strip()]
        cls["methods"].append({"name": m.group(2), "params": params, "returns": (m.group(4) or "void").strip(),
                               "visibility": vis.get(m.group(1) or "+", "public")})
        return
    m = re.match(r"^([+\-#~])?\s*(\w+)\s*:\s*(.+)$", s)
    if m:
        cls["attributes"].append({"name": m.group(2), "type": m.group(3).strip(),
                                  "visibility": vis.get(m.group(1) or "-", "private")})


def _activity_line(d: dict[str, Any], s: str) -> bool:
    act = d["activity"]
    if s in {"start", "stop", "end", "else", "endif"} or s.startswith("else "):
        act.append({"step": s.split(" ")[0], "branch": _paren(s)})
        return True
    if m := re.match(r"^:(.+);$", s):
        act.append({"step": "action", "text": m.group(1).strip()})
        return True
    if m := re.match(r"^if\s*\((.+?)\)\s*then\s*(?:\((.+?)\))?", s):
        act.append({"step": "if", "condition": m.group(1), "branch": m.group(2)})
        return True
    return False


def _paren(s: str) -> str | None:
    m = re.search(r"\((.+?)\)", s)
    return m.group(1) if m else None


def _check_types(d: dict[str, Any]) -> None:
    kinds = {e["kind"] for e in d["elements"]}
    expected = EXPECTED_TYPES.get(d["type"])
    if d["type"] == "Object" and "participant" in kinds:
        d["warnings"].append("Object diagram uses 'participant' (sequence syntax) instead of 'object'; "
                             "participants treated as objects.")
        for e in d["elements"]:
            if e["kind"] == "participant":
                e["kind"] = "object"
    elif expected and kinds and not kinds & expected:
        d["warnings"].append(f"{d['type']} diagram contains unexpected element kinds: {sorted(kinds)}")
    if d["type"] in {"Component", "Container"} and "artifact" in kinds:
        d["warnings"].append(f"{d['type']} diagram declares its parts with 'artifact' instead of "
                             f"'{d['type'].lower()}'.")
