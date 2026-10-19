import json

from sfagent.parsers.spec import build_spec, save_spec, validate_spec


def test_spec_is_schema_valid(doc_path, view_path):
    assert validate_spec(build_spec(doc_path, view_path)) == []


def test_spec_is_deterministic_for_prompt_caching(doc_path, view_path):
    a = json.dumps(build_spec(doc_path, view_path), sort_keys=True)
    b = json.dumps(build_spec(doc_path, view_path), sort_keys=True)
    assert a == b


def test_domain_model_summary(doc_path, view_path):
    dm = build_spec(doc_path, view_path)["domain_model"]
    assert dm["actors"] == ["Admin", "End User"]
    assert {"actor": "Admin", "use_case": "Update Questions"} in dm["use_cases"]
    assert [c["name"] for c in dm["classes"]] == ["Game", "Question", "User", "Admin"]
    assert dm["states"] == ["Playing", "Paused", "GameOver"]
    assert "AdminComponent" in dm["components"] and "UserComponent" in dm["components"]
    assert dm["sequences"][0]["messages"][0] == "User -> Game: play()"
    assert dm["packages"]["Game"] == ["Game", "Question"]


def test_spec_target_platform_and_issues(doc_path, view_path, tmp_path):
    spec = build_spec(doc_path, view_path)
    assert spec["target_platform"]["kind"] == "desktop"
    codes = {i["code"] for i in spec["input_issues"]}
    assert "PLATFORM_CONFLICT" in codes and "UML_SYNTAX" in codes
    out = save_spec(spec, tmp_path / "agent_run" / "spec.json")
    assert json.loads(out.read_text(encoding="utf-8"))["spec_version"] == "1.0"


def test_schema_rejects_web_target(doc_path, view_path):
    spec = build_spec(doc_path, view_path)
    spec["target_platform"]["kind"] = "web"
    assert validate_spec(spec)
