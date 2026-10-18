from app.parsers.uml_parser import parse_diagram, parse_views


def _views(view_path):
    return parse_views(view_path.read_text(encoding="utf-8"))


def _get(views, name):
    return next(d for d in views["diagrams"] if d["name"] == name)


def test_all_13_diagrams_with_views_and_types(view_path):
    views = _views(view_path)
    assert len(views["diagrams"]) == 13
    assert {d["view"] for d in views["diagrams"]} == {"Scenario", "Logic", "Process", "Development", "Physical"}
    assert _get(views, "SequenceDiagram2")["type"] == "Sequence"  # inherits the numbered title above it


def test_use_case_diagram(view_path):
    d = _get(_views(view_path), "UseCaseDiagram")
    usecases = {e["id"]: e["label"] for e in d["elements"] if e["kind"] == "usecase"}
    assert usecases == {"PlayGame": "Play Game", "ViewScore": "View Score",
                        "UpdateQuestions": "Update Questions", "ViewHelp": "View Help"}
    actors = {e["id"]: e["label"] for e in d["elements"] if e["kind"] == "actor"}
    assert actors == {"EndUser": "End User", "Admin": "Admin"}
    assert {"from": "Admin", "to": "UpdateQuestions"}.items() <= d["relations"][-1].items()


def test_class_diagram_members_and_composition(view_path):
    d = _get(_views(view_path), "ClassDiagram")
    q = next(e for e in d["elements"] if e["id"] == "Question")
    assert [a["name"] for a in q["attributes"]] == ["id", "prompt", "options"]
    assert q["attributes"][2]["type"] == "List<string>"
    admin = next(e for e in d["elements"] if e["id"] == "Admin")
    assert admin["methods"][0] == {"name": "updateQuestions", "params": ["questions: List<Question>"],
                                   "returns": "void", "visibility": "public"}
    assert all(r["kind"] == "composition" for r in d["relations"])


def test_state_diagram(view_path):
    d = _get(_views(view_path), "StateDiagram")
    assert [e["id"] for e in d["elements"]] == ["Playing", "Paused", "GameOver"]
    assert {(r["from"], r["to"], r["label"]) for r in d["relations"]} == {
        ("[*]", "Playing", None), ("Playing", "Paused", "pause()"),
        ("Paused", "Playing", "resume()"), ("Playing", "GameOver", "gameOver()")}


def test_activity_diagram(view_path):
    act = _get(_views(view_path), "ActivityDiagram")["activity"]
    assert act[0]["step"] == "start" and act[-1]["step"] == "stop"
    assert {"step": "if", "condition": "game over?", "branch": "yes"} in act


def test_tolerates_mermaid_arrows_and_object_participants(view_path):
    views = _views(view_path)
    seq = _get(views, "SequenceDiagram1")
    assert len(seq["relations"]) == 8 and seq["relations"][0]["arrow"] == "->>"
    assert any("Mermaid" in w for w in seq["warnings"])
    obj = _get(views, "ObjectDiagram")
    assert {e["kind"] for e in obj["elements"]} == {"object"}
    assert any("participant" in w for w in obj["warnings"])


def test_package_and_class_with_same_name(view_path):
    d = _get(_views(view_path), "PackageDiagram")
    classes = {(e["id"], e.get("parent")) for e in d["elements"] if e["kind"] == "class"}
    assert classes == {("Game", "Game"), ("Question", "Game"), ("User", "User"), ("Admin", "Admin")}


def test_notes_and_unknown_lines():
    d = parse_diagram(["@startuml X", "participant A", "note right of A: hello", "!weird"],
                      view=None, dtype="Sequence", title=None)
    assert d["notes"] == [{"target": "A", "text": "hello"}]
    assert d["raw"] == ["!weird"] and d["warnings"]
