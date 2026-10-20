import random

from question.question import Question
from game.game import GameService
from game.state_machine import State


def test_two_rounds_differ_with_seeded_random():
    pool = [Question(id=f"s{i}", prompt=f"p{i}", choices=["a", "b"], correct_value="a")
            for i in range(20)]
    svc = GameService(pool, random.Random(42))
    r1 = svc.play(question_count=10)
    ids1 = [q.id for q in r1.questions]
    r2 = svc.play(question_count=10)
    ids2 = [q.id for q in r2.questions]
    # order and/or membership differ; assert not identical sequences
    assert ids1 != ids2


def test_admin_added_question_can_appear_in_round(tmp_store):
    pool = tmp_store.list_questions()
    svc = GameService(pool, random.Random(1))
    custom = Question(id="admin-q", prompt="admin prompt", choices=["x", "y"], correct_value="x")
    svc.pool.append(custom)
    found = False
    for _ in range(50):
        r = svc.play(question_count=6)
        if any(q.id == "admin-q" for q in r.questions):
            found = True
            break
    assert found


def test_round_reaches_game_over_state():
    qs = [Question(id="q1", prompt="p", choices=["yes", "no"], correct_value="yes")]
    svc = GameService([], random.Random(0))
    svc.pool = []
    # directly construct a round
    from game.game import Round
    r = Round(qs)
    r.submit("yes")
    assert r.finished is True
    assert r.state_machine.state is State.GAME_OVER

def test_full_playthrough_scoring():
    qs = [Question(id=f"q{i}", prompt="p", choices=["ok", "bad"], correct_value="ok")
          for i in range(4)]
    from game.game import Round
    r = Round(qs)
    r.submit("ok")
    r.submit("bad")
    r.submit("ok")
    ended = r.submit("ok")
    assert ended is True
    assert r.correct == 3
    assert r.wrong == 1
