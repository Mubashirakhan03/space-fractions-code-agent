from question.question import Question
from game.game import Game, Round, GameService


def test_game_score_defaults_zero():
    g = Game("g1")
    assert g.view_score() == 0


def test_round_shuffles_and_counts():
    qs = [Question(id=f"q{i}", prompt=f"p{i}", choices=["a", "b"], correct_value="a")
          for i in range(4)]
    r = Round(qs)
    assert r.total == 4
    assert r.remaining == 4
    assert r.current is not None


def test_round_submit_tracks_correct_and_wrong():
    import random
    qs = [Question(id="q1", prompt="p", choices=["yes", "no"], correct_value="yes"),
          Question(id="q2", prompt="p", choices=["up", "dn"], correct_value="up")]
    r = Round(qs, random.Random(0))
    assert r.submit(r.current.correct_value) is False
    assert r.correct == 1
    assert r.submit("definitely-wrong") is True  # ended (last question)
    assert r.wrong == 1
    assert r.finished is True


def test_round_expected_available_after_submit():
    q = Question(id="q1", prompt="p", choices=["good", "bad"], correct_value="good")
    r = Round([q])
    r.submit("bad")  # wrong answer
    assert r.last_correct_answer == "good"
    assert r.last_was_correct is False


def test_game_service_play_includes_pool_and_generated():
    pool = [Question(id="s1", prompt="stored", choices=["a", "b"], correct_value="a")]
    svc = GameService(pool)
    r = svc.play(question_count=10)
    assert r.total == 10
    assert any(q.id == "s1" for q in r.questions)
