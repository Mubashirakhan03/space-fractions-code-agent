import os
import tempfile

from question.question import Question, QuestionKind
from store.database import Database


def _make_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.remove(path)
    return Database(path), path


def test_seed_only_when_empty():
    db, path = _make_db()
    try:
        qs = [Question("p1", ["a", "b"], 0), Question("p2", ["c", "d"], 0)]
        n = db.seed(qs)
        assert n == 2
        # seeding again does nothing
        assert db.seed(qs) == 0
        assert db.count_questions() == 2
    finally:
        db.close()
        os.remove(path)


def test_add_update_delete():
    db, path = _make_db()
    try:
        q = Question("Which equals 1/2?", ["2/4", "1/3"], 0,
                     kind=QuestionKind.EQUIVALENT, qid="q1")
        db.add_question(q)
        assert db.get_question("q1").prompt == q.prompt
        q2 = Question("updated", ["x", "y", "z"], 0, qid="q1")
        db.update_question(q2)
        assert db.get_question("q1").prompt == "updated"
        db.delete_question("q1")
        assert db.get_question("q1") is None
    finally:
        db.close()
        os.remove(path)


def test_record_and_list_games():
    from game.game import Game
    db, path = _make_db()
    try:
        g = Game([Question("p", ["a", "b"], 0)])
        g.submit("a")
        db.record_game(g)
        games = db.all_games()
        assert len(games) == 1
        assert games[0]["score"] == 1
        assert games[0]["total"] == 1
    finally:
        db.close()
        os.remove(path)


def test_settings():
    db, path = _make_db()
    try:
        assert db.get_setting("admin_pin", "1234") == "1234"
        db.set_setting("admin_pin", "9999")
        assert db.get_setting("admin_pin") == "9999"
    finally:
        db.close()
        os.remove(path)
