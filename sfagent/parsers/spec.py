"""Combine both parsed inputs into one `spec.json` — the agent's structured input.

The spec contains no timestamps or random values so it is byte-identical across runs; it sits at
the start of every prompt, which keeps DeepSeek's automatic prefix cache hitting.

CLI (preview): python -m app.parsers.spec <Architecture_Documentation.md> <Architecture_View.md> [out.json]
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from sfagent.parsers.doc_parser import parse_document
from sfagent.parsers.uml_parser import parse_views

SPEC_VERSION = "1.0"
SCHEMA_PATH = Path(__file__).resolve().parent.parent.parent / "schemas" / "spec.schema.json"

TARGET_PLATFORM = {
    "kind": "desktop",
    "os": "Windows",
    "gui": "tkinter",
    "language": "Python 3.11+",
    "dependencies": "Python standard library only (see bundled module list) + pytest for tests",
    "persistence": "SQLite file",
    "users": "single local user per session",
    "source": "Task constraint: the deliverable must be a Windows desktop application, not web-based.",
}


def _source(path: Path, text: str) -> dict[str, str]:
    return {"file": path.name, "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}


def domain_model(doc: dict[str, Any], views: dict[str, Any]) -> dict[str, Any]:
    """Compact, LLM-friendly summary of what the diagrams say."""
    by_type: dict[str, list[dict[str, Any]]] = {}
    for d in views["diagrams"]:
        by_type.setdefault(d["type"], []).append(d)

    def first(t: str) -> dict[str, Any]:
        return (by_type.get(t) or [{"elements": [], "relations": [], "activity": []}])[0]

    uc = first("UseCase")
    actor_label = {e["id"]: e["label"] for e in uc["elements"] if e["kind"] == "actor"}
    usecase_label = {e["id"]: e["label"] for e in uc["elements"] if e["kind"] == "usecase"}
    use_cases = [
        {"actor": actor_label.get(r["from"], r["from"]), "use_case": usecase_label.get(r["to"], r["to"])}
        for r in uc["relations"]
    ]
    classes = [
        {"name": e["id"], "attributes": e["attributes"], "methods": e["methods"]}
        for e in first("Class")["elements"] if e["kind"] == "class"
    ]
    st = first("State")
    sequences = [
        {"name": d["name"], "messages": [f"{r['from']} -> {r['to']}: {r['label']}" for r in d["relations"]]}
        for d in by_type.get("Sequence", [])
    ]
    packages: dict[str, list[str]] = {}
    for e in first("Package")["elements"]:
        if e["kind"] == "class" and e.get("parent"):
            packages.setdefault(e["parent"], []).append(e["id"])
    return {
        "actors": sorted(actor_label.values()),
        "use_cases": use_cases,
        "classes": classes,
        "class_relations": [f"{r['from']} {r['arrow']} {r['to']} ({r['kind']})" for r in first("Class")["relations"]],
        "states": [e["id"] for e in st["elements"] if e["kind"] == "state"],
        "transitions": [{"from": r["from"], "to": r["to"], "trigger": r["label"]} for r in st["relations"]],
        "activity": first("Activity")["activity"],
        "sequences": sequences,
        "packages": packages,
        "components": sorted({e["id"] for e in first("Component")["elements"]}
                             | {c["name"] for c in doc["components"]}),
        "implied_features": doc["implied_features"],
    }


def build_spec(doc_path: Path, view_path: Path) -> dict[str, Any]:
    doc_text = Path(doc_path).read_text(encoding="utf-8")
    view_text = Path(view_path).read_text(encoding="utf-8")
    doc = parse_document(doc_text)
    views = parse_views(view_text)
    issues = list(doc["issues"]) + [
        {"code": "UML_SYNTAX", "severity": "low", "message": w} for w in views["warnings"]
    ]
    return {
        "spec_version": SPEC_VERSION,
        "sources": {"documentation": _source(Path(doc_path), doc_text),
                    "views": _source(Path(view_path), view_text)},
        "target_platform": TARGET_PLATFORM,
        "domain_model": domain_model(doc, views),
        "requirements": doc["requirements"],
        "input_issues": issues,
        "platform_conflicts": doc["platform_terms"],
        "document": doc,
        "views": views,
    }


def validate_spec(spec: dict[str, Any]) -> list[str]:
    """Validate against schemas/spec.schema.json; returns error messages (empty = valid)."""
    import jsonschema

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    return [f"{'/'.join(map(str, e.path))}: {e.message}" for e in validator.iter_errors(spec)]


def save_spec(spec: dict[str, Any], out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    spec = build_spec(Path(argv[0]), Path(argv[1]))
    errors = validate_spec(spec)
    if len(argv) > 2:
        save_spec(spec, Path(argv[2]))
    print(json.dumps({"domain_model": spec["domain_model"], "issues": len(spec["input_issues"]),
                      "schema_errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
