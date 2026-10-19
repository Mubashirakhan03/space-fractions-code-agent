"""Verify's import check catches wrong imports in main.py and modules that tests never import."""

from sfagent.agent.import_check import run_import_check
from sfagent.tools.runner import PythonRunner


def project(tmp_path, main_src: str, widgets_src: str = "def styled():\n    return 1\n"):
    (tmp_path / "ui").mkdir()
    (tmp_path / "ui" / "__init__.py").write_text("")
    (tmp_path / "ui" / "widgets.py").write_text(widgets_src)
    (tmp_path / "main.py").write_text(main_src)
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("from missing_module import nothing\n")  # tests are skipped
    return PythonRunner(tmp_path, tmp_path / "agent_run", timeout=60)


GOOD_MAIN = '''from ui.widgets import styled


def main():
    raise SystemExit("main() must not run during the import check")


if __name__ == "__main__":
    main()
'''


def test_wrong_name_imported_by_main_is_caught(tmp_path):
    ok, report = run_import_check(project(tmp_path, GOOD_MAIN.replace("import styled", "import centered")))
    assert not ok
    assert "main.py: ImportError: cannot import name 'centered' from 'ui.widgets'" in report


def test_good_project_passes_and_main_is_not_run(tmp_path):
    ok, report = run_import_check(project(tmp_path, GOOD_MAIN))
    assert ok, report
    assert "incl. main.py" in report


def test_broken_module_that_no_test_imports_is_caught(tmp_path):
    ok, report = run_import_check(project(tmp_path, GOOD_MAIN, widgets_src="import tkinter.nonexistent\n"))
    assert not ok and "ui/widgets.py" in report
