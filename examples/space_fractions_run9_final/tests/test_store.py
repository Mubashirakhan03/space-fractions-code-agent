import json

from question.question import Question


def test_fresh_store_is_seeded(seed_json):
    from store.store import QuestionStore
    import tempfile, os
    from pathlib import Path
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    st = QuestionStore(Path(path), seed_json=seed_json)
    try:
        qs = st.list_questions()
        assert len(qs) >= 20
        kinds = {q.kind for q in qs}
        assert len(kinds) >= 4
    finally:
        st.close()
        os.remove(path)


def test_seed_loaded_only_when_empty(seed_json):
    from store.store import QuestionStore
    import tempfile, os
    from pathlib import Path
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    st = QuestionStore(Path(path), seed_json=seed_json)
    seeded_count = st.count()
    st.add_question(Question(id="custom", prompt="mine", correct_value="1/2", choices=[]))
    st.close()
    st2 = QuestionStore(Path(path), seed_json=seed_json)
    try:
        qs = st2.list_questions()
        # should NOT re-seed (the seed only loads when the store is empty)
        assert len(qs) == seeded_count + 1
        assert any(q.id == "custom" for q in qs)
    finally:
        st2.close()
        os.remove(path)


def test_add_update_delete(tmp_store):
    q = Question(id="x1", prompt="prompt", correct_value="1/2", choices=["1/2", "1/3"])
    tmp_store.add_question(q)
    assert tmp_store.get_question("x1") is not None
    q.prompt = "edited"
    tmp_store.update_question(q)
    assert tmp_store.get_question("x1").prompt == "edited"
    assert tmp_store.delete_question("x1") is True
    assert tmp_store.get_question("x1") is None
    assert tmp_store.delete_question("x1") is False
