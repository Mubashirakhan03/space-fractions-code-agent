"""Parse `Architecture_Documentation.md` into structured JSON.

Extracts the section tree (A–L), markdown tables as row objects, fenced code blocks (YAML/OpenAPI/
Kubernetes parsed with PyYAML, CSV rows, SQL tables, proto services), requirement ids, components,
tech stack, assumptions, open questions, deliverables, and detects input-quality issues.
Everything is deterministic so the result is reproducible and testable without an LLM.
"""

from __future__ import annotations

import csv
import hashlib
import io
import re
from typing import Any

import yaml

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
SECTION_ID_RE = re.compile(r"^([A-Z])\.\s+(.*)$")
FENCE_RE = re.compile(r"^```\s*([\w+-]*)\s*$")
REQ_ID_RE = re.compile(r"\b((?:FR|NFR|ASR)-\d+)\b")
BULLET_RE = re.compile(r"^\s*[*\-]\s+(.*)$")
NUMBERED_RE = re.compile(r"^\s*\d+\.\s+(.*)$")
ASSUMPTION_RE = re.compile(r"^\s*(A\d+)\s*:\s*(.+)$")

LANG_ALIASES = {"yml": "yaml", "md": "markdown", "postgres": "sql", "protobuf": "proto"}

# Terms that only make sense for a distributed web/cloud system (desktop-target conflict check).
WEB_CLOUD_TERMS = [
    "web-based", "microservices", "cloud", "Kubernetes", "Node.js", "Express.js", "PostgreSQL", "Redis",
    "RabbitMQ", "Elasticsearch", "OAuth2", "Prometheus", "Jenkins", "Docker", "Terraform", "Istio",
    "Vault", "load balancing", "autoscaling", "RESTful", "gRPC", "TLS", "replicas",
]


def _norm_lang(lang: str) -> str:
    lang = lang.lower()
    return LANG_ALIASES.get(lang, lang)


def parse_table(lines: list[str]) -> list[dict[str, str]]:
    """Markdown table lines → list of row dicts keyed by header (separator row skipped)."""
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines]
    if len(rows) < 2:
        return []
    header = rows[0]
    body = [r for r in rows[1:] if not all(re.fullmatch(r":?-{2,}:?", c) for c in r if c)]
    return [{header[i]: (r[i] if i < len(r) else "") for i in range(len(header))} for r in body]


def _parse_code(lang: str, code: str) -> dict[str, Any]:
    """Interpret a fenced code block by language. Errors are recorded, never raised."""
    block: dict[str, Any] = {"language": lang, "content": code, "kind": lang or "text"}
    try:
        if lang == "yaml":
            data = yaml.safe_load(code)
            block["parsed"] = data
            if isinstance(data, dict) and "openapi" in data:
                block["kind"] = "openapi"
                block["paths"] = sorted((data.get("paths") or {}).keys())
            elif isinstance(data, dict) and {"apiVersion", "kind"} <= data.keys():
                block["kind"] = "kubernetes"
        elif lang == "csv":
            block["rows"] = list(csv.DictReader(io.StringIO(code)))
        elif lang == "sql":
            block["tables"] = re.findall(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)", code, re.I)
        elif lang == "proto":
            block["services"] = re.findall(r"service\s+(\w+)", code)
            block["rpcs"] = re.findall(r"rpc\s+(\w+)", code)
            block["messages"] = re.findall(r"message\s+(\w+)", code)
        elif lang == "markdown":
            block["kind"] = "file_list"
            block["items"] = [ln.strip() for ln in code.splitlines() if ln.strip()]
    except (yaml.YAMLError, csv.Error) as exc:
        block["parse_error"] = str(exc)
    return block


def _new_node(level: int, title: str) -> dict[str, Any]:
    node: dict[str, Any] = {"level": level, "title": title, "_lines": [], "code_blocks": [], "children": []}
    m = SECTION_ID_RE.match(title)
    if level == 1 and m:
        node["id"], node["title"] = m.group(1), m.group(2)
    return node


def _split_sections(text: str) -> tuple[str, list[dict[str, Any]]]:
    """Build a heading tree. Lines inside code fences never count as headings."""
    preamble: list[str] = []
    roots: list[dict[str, Any]] = []
    stack: list[dict[str, Any]] = []
    fence_lang: str | None = None
    fence_buf: list[str] = []
    for line in text.splitlines():
        fence = FENCE_RE.match(line.strip())
        if fence_lang is not None:
            if line.strip() == "```":
                block = _parse_code(fence_lang, "\n".join(fence_buf))
                (stack[-1]["code_blocks"] if stack else []).append(block)
                fence_lang, fence_buf = None, []
            else:
                fence_buf.append(line)
            continue
        if fence:
            fence_lang = _norm_lang(fence.group(1))
            continue
        h = HEADING_RE.match(line)
        if h:
            node = _new_node(len(h.group(1)), h.group(2))
            while stack and stack[-1]["level"] >= node["level"]:
                stack.pop()
            (stack[-1]["children"] if stack else roots).append(node)
            stack.append(node)
        elif stack:
            stack[-1]["_lines"].append(line)
        else:
            preamble.append(line)
    return "\n".join(preamble).strip(), roots


def _finish_node(node: dict[str, Any]) -> None:
    """Turn raw lines into text, tables and bullet lists (recursively)."""
    lines = node.pop("_lines")
    tables: list[list[dict[str, str]]] = []
    text_lines: list[str] = []
    buf: list[str] = []
    for ln in [*lines, ""]:
        if ln.strip().startswith("|"):
            buf.append(ln)
            continue
        if buf:
            tables.append(parse_table(buf))
            buf = []
        text_lines.append(ln)
    node["text"] = "\n".join(text_lines).strip()
    node["tables"] = tables
    node["bullets"] = [m.group(1).strip() for ln in text_lines if (m := BULLET_RE.match(ln))]
    node["numbered"] = [m.group(1).strip() for ln in text_lines if (m := NUMBERED_RE.match(ln))]
    for child in node["children"]:
        _finish_node(child)


def _walk(nodes: list[dict[str, Any]]):
    for n in nodes:
        yield n
        yield from _walk(n["children"])


def _section_of(roots: list[dict[str, Any]], node: dict[str, Any]) -> str:
    for root in roots:
        if node is root or any(node is n for n in _walk(root["children"])):
            return root.get("id", root["title"])
    return "?"


def parse_document(text: str) -> dict[str, Any]:
    """Main entry point: markdown text → structured dict (see schemas/spec.schema.json `document`)."""
    preamble, roots = _split_sections(text)
    for r in roots:
        _finish_node(r)
    nodes = list(_walk(roots))

    all_tables = [(n, t) for n in nodes for t in n["tables"] if t]
    all_blocks = [(n, b) for n in nodes for b in n["code_blocks"]]

    def find_table(*cols: str) -> list[dict[str, str]]:
        for _, t in all_tables:
            if all(c in t[0] for c in cols):
                return t
        return []

    traceability = find_table("Requirement ID", "Component(s)")
    requirements: dict[str, dict[str, Any]] = {}
    for row in traceability:
        rid = row["Requirement ID"]
        requirements[rid] = {
            "id": rid,
            "type": rid.split("-")[0],
            "short_text": row.get("Short Text", ""),
            "diagrams": _split_list(row.get("Diagram(s)", "")),
            "components": _split_list(row.get("Component(s)", "")),
            "artifacts": _split_list(row.get("Artifact filename(s)", "")),
            "rationale": row.get("Rationale", ""),
        }
    for n in nodes:  # requirement ids mentioned anywhere (e.g. ASR-2 only in QA mapping)
        for rid in REQ_ID_RE.findall(n["text"] + str(n["tables"])):
            requirements.setdefault(rid, {"id": rid, "type": rid.split("-")[0], "short_text": "",
                                          "diagrams": [], "components": [], "artifacts": [], "rationale": ""})
            requirements[rid].setdefault("mentioned_in", [])
            sec = _section_of(roots, n)
            if sec not in requirements[rid]["mentioned_in"]:
                requirements[rid]["mentioned_in"].append(sec)

    components = []
    tech_stack = []
    for n in nodes:
        sec = _section_of(roots, n)
        for b in n["bullets"]:
            m = re.match(r"^(\w*Component)\s*:\s*(.+)$", b)
            if m:
                components.append({"name": m.group(1), "responsibility": m.group(2)})
            t = re.match(r"^([^:]+):\s*(.+?)\s*\(Justification:\s*(.+)\)\s*$", b)
            if t and sec == "D":
                tech_stack.append({"category": t.group(1), "choice": t.group(2), "justification": t.group(3)})

    assumptions = [
        {"id": m.group(1), "text": m.group(2).strip()}
        for n in nodes for ln in n["text"].splitlines() if (m := ASSUMPTION_RE.match(ln))
    ]
    open_questions = [b for n in nodes if "unresolved" in n["title"].lower() for b in n["bullets"]]
    deliverables = next((b["items"] for _, b in all_blocks if b["kind"] == "file_list"), [])

    summary_node = next((r for r in roots if r.get("id") == "A"), None)
    features = _implied_features(summary_node["text"] if summary_node else "")

    doc = {
        "preamble": preamble,
        "sections": [_public(r) for r in roots],
        "requirements": sorted(requirements.values(), key=lambda r: (r["type"], r["id"])),
        "traceability": traceability,
        "risks": find_table("Risk", "Mitigation"),
        "qa_mapping": find_table("ASR/NFR ID", "Test Type"),
        "testing_matrix": find_table("Test Type", "GameComponent"),
        "components": _dedupe(components, "name"),
        "tech_stack": tech_stack,
        "assumptions": assumptions,
        "open_questions": open_questions,
        "deliverables": deliverables,
        "implied_features": features,
        "code_blocks": [{"section": _section_of(roots, n), **_block_summary(b)} for n, b in all_blocks],
    }
    doc["platform_terms"] = _platform_terms(nodes, roots)
    doc["issues"] = detect_issues(doc, all_tables, all_blocks)
    return doc


def _implied_features(summary: str) -> list[str]:
    """Features listed in the executive summary ("consists of a, b, c, and d")."""
    m = re.search(r"consists of (.+?)\.", summary)
    if not m:
        return []
    parts = re.split(r",\s*(?:and\s+)?|\s+and\s+", m.group(1))
    return [re.sub(r"^(an?|the)\s+", "", p.strip()) for p in parts if p.strip()]


def _platform_terms(nodes, roots) -> list[dict[str, Any]]:
    found: dict[str, set[str]] = {}
    for n in nodes:
        haystack = n["title"] + "\n" + n["text"] + "\n" + "\n".join(b["content"] for b in n["code_blocks"])
        for term in WEB_CLOUD_TERMS:
            if re.search(rf"(?<![\w-]){re.escape(term)}(?![\w-])", haystack, re.I):
                found.setdefault(term, set()).add(_section_of(roots, n))
    return [{"term": t, "sections": sorted(s)} for t, s in found.items()]


def detect_issues(doc: dict[str, Any], all_tables, all_blocks) -> list[dict[str, str]]:
    """Deterministic input-quality checks. The agent copies these into DESIGN_DECISIONS.md."""
    issues: list[dict[str, str]] = []

    def add(code: str, severity: str, message: str) -> None:
        issues.append({"code": code, "severity": severity, "message": message})

    for node, table in all_tables:
        cols = list(table[0].keys())[1:]
        if cols and all(not row[c] for row in table for c in cols):
            add("EMPTY_TABLE", "high", f"Table under '{node['title']}' has headers but every cell is empty.")

    listed = set(doc["deliverables"])
    for req in doc["requirements"]:
        for art in req["artifacts"]:
            if "/" in art and art not in listed:
                add("ARTIFACT_MISMATCH", "medium",
                    f"{req['id']} references '{art}' but the deliverables list does not contain it "
                    f"(deliverables: {', '.join(sorted(a for a in listed if '/' in a))}).")

    ids = [r["id"] for r in doc["requirements"]]
    if len(ids) < 6:
        add("THIN_REQUIREMENTS", "high",
            f"Only {len(ids)} requirement ids exist ({', '.join(ids)}); game features from the summary "
            f"({', '.join(doc['implied_features'])}) have no FR of their own.")
    untraced = [r["id"] for r in doc["requirements"] if not r["components"]]
    if untraced:
        add("UNTRACED_REQUIREMENT", "medium", f"Not in the traceability matrix: {', '.join(untraced)}.")

    justs = [t["justification"] for t in doc["tech_stack"]]
    if len(justs) >= 5 and len(set(justs)) <= 3:
        add("GENERIC_JUSTIFICATIONS", "medium",
            f"{len(justs)} technology choices share only {len(set(justs))} copy-pasted justifications "
            f"(e.g. '{justs[-3]}' for {doc['tech_stack'][-3]['choice']}).")

    hashes: dict[str, int] = {}
    for _, b in all_blocks:
        h = hashlib.sha1(b["content"].encode()).hexdigest()
        hashes[h] = hashes.get(h, 0) + 1
    dupes = sum(1 for c in hashes.values() if c > 1)
    if dupes:
        add("DUPLICATE_BLOCKS", "low", f"{dupes} code block(s) are duplicated verbatim (section L repeats D/E).")

    for _, b in all_blocks:
        if b.get("parse_error"):
            add("CODE_PARSE_ERROR", "medium", f"{b['language']} block could not be parsed: {b['parse_error']}")

    if doc["platform_terms"]:
        terms = ", ".join(t["term"] for t in doc["platform_terms"][:10])
        add("PLATFORM_CONFLICT", "high",
            f"Document targets a web/cloud microservice system ({terms}…) but the required deliverable "
            "is a single-user desktop application.")
    return issues


def _split_list(value: str) -> list[str]:
    return [v.strip() for v in re.split(r"[,;]", value) if v.strip()]


def _dedupe(items: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    seen: set[str] = set()
    return [i for i in items if not (i[key] in seen or seen.add(i[key]))]


def _block_summary(b: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in b.items() if k != "parsed"}


def _public(node: dict[str, Any]) -> dict[str, Any]:
    out = {k: v for k, v in node.items() if k not in {"children", "code_blocks"}}
    out["code_block_kinds"] = [b["kind"] for b in node["code_blocks"]]
    out["children"] = [_public(c) for c in node["children"]]
    return out
