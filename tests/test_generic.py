"""The agent is generic: nothing about Space Fractions lives in code; profiles are optional data files."""

import re
import sys

import pytest

from app.agent import prompts
from app.agent.loop import Agent
from app.agent.profile import load_profile, parse_profile
from app.bundled import BUNDLED_STDLIB
from app.config import AppConfig
from app.gui import controller
from app.llm.mock import MockProvider, reply, tool_call
from app.parsers.spec import build_spec, validate_spec
from tests.conftest import ROOT, SAMPLES

LIB = SAMPLES / "library_tracker"
SF_PROFILE = ROOT / "profiles" / "space_fractions.md"


@pytest.fixture(scope="module")
def lib_spec():
    return build_spec(LIB / "Architecture_Documentation.md", LIB / "Architecture_View.md")


SPECIFIC_WORDS = ["space fractions", "space", "star", "planet", "rocket", "child", "children", "kid", "fraction", "6th",
                  "grade", "game", "question", "score", "player", "intro", "confetti", "pupil", "student",
                  "questions.json", "gamecomponent"]


@pytest.mark.parametrize("term", SPECIFIC_WORDS)
def test_system_prompt_has_no_task_specific_content(term):
    """The generic prompt must not carry Space-Fractions style or content; that lives in profiles/."""
    text = prompts.SYSTEM_PROMPT.lower().replace(", ".join(BUNDLED_STDLIB).lower(), "")  # e.g. module 'fractions'
    assert re.search(rf"\b{re.escape(term)}s?\b", text) is None, f"'{term}' found in the generic system prompt"


def test_plan_requires_ui_design_brief():
    assert "UI design brief" in prompts.PLAN_INSTRUCTIONS and "UI design brief" in prompts.OUTPUT_CONTRACT
    assert "UI design brief" in prompts.IMPLEMENT_INSTRUCTIONS


def test_profile_parsing():
    p = load_profile(SF_PROFILE)
    assert p.name == "Space Fractions"
    assert p.required_files == ["sql/schema.sql", "data/questions.json"]
    assert "fractions.Fraction" in p.hints
    plain = parse_profile("just some hints", source="mine.md")
    assert plain.name == "mine" and plain.required_files == []
    with pytest.raises(ValueError):
        parse_profile("---\nrequired_files: nope\n---\nx")


def test_profile_goes_into_spec_message_and_keeps_system_prompt_identical(lib_spec):
    without = prompts.initial_messages(lib_spec)
    with_p = prompts.initial_messages(lib_spec, load_profile(SF_PROFILE))
    assert without[0] == with_p[0]  # system prompt identical → same cache prefix
    assert "Task profile" not in without[1]["content"]
    assert "Task profile: Space Fractions" in with_p[1]["content"]
    assert "Architecture_Documentation.md and Architecture_View.md" in without[1]["content"]


def test_second_sample_parses_into_valid_spec(lib_spec):
    assert validate_spec(lib_spec) == []
    dm = lib_spec["domain_model"]
    assert [c["name"] for c in dm["classes"]] == ["Book", "Member", "Loan"]
    assert dm["states"] == ["Available", "Borrowed", "Overdue"]
    assert {"actor": "Librarian", "use_case": "View Overdue Report"} in dm["use_cases"]
    codes = {i["code"] for i in lib_spec["input_issues"]}
    assert {"PLATFORM_CONFLICT", "ARTIFACT_MISMATCH", "UNTRACED_REQUIREMENT", "EMPTY_TABLE", "UML_SYNTAX"} <= codes
    assert lib_spec["document"]["testing_matrix"]  # found generically (no component name hard-coded)


def library_project():
    return [
        {"path": "main.py", "content": "from loans.loan import Loan\n\nif __name__ == '__main__':\n    print(Loan)\n"},
        {"path": "loans/__init__.py", "content": ""},
        {"path": "loans/loan.py", "content": "class Loan:\n    def daysLate(self, late=0):\n        return late\n"},
        {"path": "tests/test_loan.py",
         "content": "from loans.loan import Loan\n\n\ndef test_days_late():\n    assert Loan().daysLate(2) == 2\n"},
        {"path": "tests/test_ui_smoke.py",
         "content": "def test_ui_stub():\n    minsize = (1100, 750)\n    assert minsize >= (1100, 750)\n"},
        {"path": "README.md", "content": "# Library Book Tracker\n"},
        {"path": "requirements.txt", "content": "pytest\n"},
        {"path": "TRACEABILITY.csv", "content": "requirement,use_case_or_feature,component,file,test\n"},
    ]


def library_script():
    design = ("# Design decisions\n\n## UI design brief\nClean, calm, table based.\n\n"
              "| Original | Desktop | Reason |\n|---|---|---|\n"
              + "| PostgreSQL | SQLite | local |\n" * 8)
    return [
        reply(tool_call("update_todos", "t", todos=[{"content": "build", "status": "in_progress"}]),
              tool_call("submit_plan", "p", design_decisions=design, file_tree=[f["path"] for f in library_project()])),
        reply(tool_call("write_files", "w", files=library_project())),
        reply(tool_call("finish", "f", summary="ok")),
    ]


def test_mock_agent_builds_a_different_application(tmp_path, lib_spec):
    mock = MockProvider(library_script())
    result = Agent(mock, AppConfig(provider="mock"), tmp_path / "lib", lib_spec).run()
    assert result.status == "completed" and result.verify_ok is True
    first = mock.requests[0]["messages"]
    assert "Book" in first[1]["content"] and "Space Fractions" not in first[1]["content"]
    report = (tmp_path / "lib" / "agent_run" / "RUN_REPORT.md").read_text(encoding="utf-8")
    assert "(none — spec only)" in report


def test_profile_required_files_are_enforced(tmp_path, lib_spec):
    agent = Agent(MockProvider(library_script()), AppConfig(provider="mock", fix_rounds=0), tmp_path / "p",
                  lib_spec, profile=load_profile(SF_PROFILE))
    result = agent.run()
    assert result.verify_ok is False
    assert "data/questions.json" in agent.state.verify_report


def test_frozen_resources_are_copied_out_of_temp_bundle(tmp_path, monkeypatch):
    bundle = tmp_path / "_MEI123"
    (bundle / "samples").mkdir(parents=True)
    (bundle / "samples" / controller.DOC_NAME).write_text("d")
    (bundle / "samples" / controller.VIEW_NAME).write_text("v")
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "exe_dir" / "SpaceFractionsAgent.exe"))
    monkeypatch.setattr(controller, "APP_ROOT", bundle)
    monkeypatch.setattr(controller, "user_data_dir", lambda: tmp_path / "Documents" / "SpaceFractionsAgent")
    monkeypatch.chdir(tmp_path)
    doc, view = controller.find_default_inputs()
    assert "_MEI" not in doc and doc.startswith(str(tmp_path / "Documents"))
    assert (tmp_path / "Documents" / "SpaceFractionsAgent" / "samples" / controller.VIEW_NAME).exists()


def test_list_profiles_dev_mode():
    assert SF_PROFILE in controller.list_profiles()


def test_rule_capture_message_data_before_state_change():
    assert "BEFORE you advance or mutate" in prompts.RULES
    assert "wrong-input path" in prompts.RULES and "WRONG form" in prompts.UI_QUALITY


def test_rules_from_run3_findings():
    assert "NEVER mix pack and grid" in prompts.UI_QUALITY
    assert "ONE complete flow" in prompts.UI_QUALITY and "report_callback_exception" in prompts.UI_QUALITY
    assert "delete_file" in prompts.TOOL_USAGE and "must not create, modify or delete" in prompts.TOOL_USAGE


def test_rule_visible_submit_button_and_min_size_probe():
    assert "every text input has a clearly visible Submit/Check button" in prompts.UI_QUALITY
    assert "AND at the minimum size (1100x750)" in prompts.UI_QUALITY


def test_rules_complete_forms_seed_data_and_title():
    assert "include an input for EVERY field" in prompts.UI_QUALITY
    assert "Never fill a required field silently" in prompts.UI_QUALITY
    assert "Never ship empty" in prompts.UI_QUALITY and "at least 20" in prompts.UI_QUALITY
    assert 'never the default "tk"' in prompts.UI_QUALITY


def test_profile_asks_for_generated_items_and_seed_set():
    hints = load_profile(SF_PROFILE).hints
    assert "at least 20 seed questions" in hints and "generates NEW fraction questions in code" in hints


def test_rule_random_rounds_and_generated_items():
    ui = prompts.UI_QUALITY
    assert "draws its items at RANDOM from the whole pool" in ui and "SHUFFLES" in ui
    assert "items added by an admin" in ui
    assert "If the content is" in ui and "generates new items in code" in ui
    assert "never equal to" in ui and "two rounds differ" in ui
