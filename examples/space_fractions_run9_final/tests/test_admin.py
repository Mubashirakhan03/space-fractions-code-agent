from question.question import Question
from admin.admin import QuestionRepository
from admin.settings import Settings


def _temp_settings():
    import tempfile, os
    from pathlib import Path
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    return Path(path)


def test_repository_crud(tmp_store):
    repo = QuestionRepository(tmp_store)
    initial = len(repo.list_all())
    q = Question(id="adm1", prompt="p", correct_value="1/4", choices=["1/4", "1/2"])
    repo.add(q)
    assert len(repo.list_all()) == initial + 1
    q.prompt = "changed"
    repo.update(q)
    assert repo.store.get_question("adm1").prompt == "changed"
    assert repo.delete("adm1") is True

def test_settings_default_pin(tmp_path):
    s = Settings(tmp_path / "settings.json")
    s.load()
    assert s.admin_pin == "4321"
    assert s.check_pin("4321") is True
    assert s.check_pin("9999") is False
