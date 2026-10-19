from sfagent.parsers.doc_parser import parse_document, parse_table


def _doc(doc_path):
    return parse_document(doc_path.read_text(encoding="utf-8"))


def test_sections_a_to_l(doc_path):
    ids = [s.get("id") for s in _doc(doc_path)["sections"] if s.get("id")]
    assert ids == list("ABCDEFGHIJKL")


def test_requirements_and_traceability(doc_path):
    doc = _doc(doc_path)
    reqs = {r["id"]: r for r in doc["requirements"]}
    assert set(reqs) == {"FR-1", "NFR-1", "ASR-1", "ASR-2"}
    assert reqs["FR-1"]["components"] == ["GameComponent"]
    assert reqs["ASR-1"]["artifacts"] == ["sql/question_ddl.sql"]
    assert len(doc["traceability"]) == 3


def test_components_features_assumptions(doc_path):
    doc = _doc(doc_path)
    assert [c["name"] for c in doc["components"]] == ["GameComponent", "QuestionComponent", "UserComponent"]
    assert doc["implied_features"] == ["introductory movie", "main menu", "series of fraction questions",
                                       "ending scene with feedback"]
    assert [a["id"] for a in doc["assumptions"]] == ["A1", "A2"]
    assert len(doc["open_questions"]) == 2
    assert "sql/game_ddl.sql" in doc["deliverables"]


def test_code_blocks_are_interpreted(doc_path):
    doc = _doc(doc_path)
    kinds = [b["kind"] for b in doc["code_blocks"]]
    assert {"openapi", "proto", "sql", "kubernetes", "csv", "file_list"} <= set(kinds)
    openapi = next(b for b in doc["code_blocks"] if b["kind"] == "openapi")
    assert openapi["paths"] == ["/play"]
    sql = next(b for b in doc["code_blocks"] if b["kind"] == "sql")
    assert sql["tables"] == ["games"]
    csv_rows = next(b for b in doc["code_blocks"] if b["kind"] == "csv")["rows"]
    assert csv_rows[0]["Requirement ID"] == "FR-1"


def test_all_known_input_traps_detected(doc_path):
    codes = {i["code"] for i in _doc(doc_path)["issues"]}
    assert {"EMPTY_TABLE", "ARTIFACT_MISMATCH", "THIN_REQUIREMENTS", "GENERIC_JUSTIFICATIONS",
            "DUPLICATE_BLOCKS", "PLATFORM_CONFLICT", "UNTRACED_REQUIREMENT"} <= codes


def test_platform_terms_found(doc_path):
    terms = {t["term"] for t in _doc(doc_path)["platform_terms"]}
    assert {"microservices", "PostgreSQL", "Kubernetes", "Redis", "RabbitMQ"} <= terms


def test_headings_inside_code_fences_are_ignored():
    doc = parse_document("# A. Title\n```markdown\n# not a heading\n```\ntext\n")
    assert len(doc["sections"]) == 1
    assert doc["sections"][0]["children"] == []


def test_parse_table_handles_short_rows():
    rows = parse_table(["| a | b |", "| --- | --- |", "| 1 |"])
    assert rows == [{"a": "1", "b": ""}]


def test_bad_yaml_is_reported_not_raised():
    doc = parse_document("# A. X\n```yml\nkey: [unclosed\n```\n")
    assert any(i["code"] == "CODE_PARSE_ERROR" for i in doc["issues"])
