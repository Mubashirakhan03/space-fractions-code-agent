"""Requirements the harness derives from the spec: named scenes, animated scene, protected roles."""

from pathlib import Path

from sfagent.agent import prompts, spec_rules
from sfagent.parsers.spec import build_spec

ROOT = Path(__file__).resolve().parent.parent


def _spec(folder: Path) -> dict:
    return build_spec(folder / "Architecture_Documentation.md", folder / "Architecture_View.md")


def test_space_fractions_spec_needs_animation_and_admin_pin():
    rules = spec_rules.derive(_spec(ROOT / "samples"))
    assert rules.animation == ["introductory movie"]
    assert rules.protected_roles == ["Admin"]
    assert "introductory movie" in rules.screens and "ending scene with feedback" in rules.screens
    assert "Update Questions" in rules.use_cases
    assert rules.to_probe() == {"animation": ["introductory movie"], "protected_roles": ["Admin"]}


def test_library_spec_has_no_animation_or_protected_role():
    rules = spec_rules.derive(_spec(ROOT / "samples" / "library_tracker"))
    assert rules.animation == [] and rules.protected_roles == []
    block = spec_rules.checklist(rules)
    assert "overdue report" in block and "Animated scene" not in block and "PIN" not in block


def test_animation_phrases_are_found_generically():
    spec = {"document": {"sections": [{"text": "The app opens with an animated logo and a splash screen."}]},
            "domain_model": {"actors": ["Operator", "Visitor"], "use_cases": []}}
    rules = spec_rules.derive(spec)
    assert any("animated logo" in a for a in rules.animation) and any("splash screen" in a for a in rules.animation)
    assert rules.protected_roles == ["Operator"]
    assert spec_rules.checklist(spec_rules.derive({})) == ""


def test_checklist_goes_into_the_first_user_message_not_the_system_prompt():
    msgs = prompts.initial_messages(_spec(ROOT / "samples"))
    user = msgs[1]["content"]
    assert "# Harness checklist" in user and "'introductory movie'" in user and "Protected role(s): Admin" in user
    lib = prompts.initial_messages(_spec(ROOT / "samples" / "library_tracker"))
    assert lib[0] == msgs[0]  # same system prompt for every spec → stable cache prefix
    system = msgs[0]["content"]
    assert "Animated scenes:" in system and "Protected roles:" in system and "Spec coverage:" in system
