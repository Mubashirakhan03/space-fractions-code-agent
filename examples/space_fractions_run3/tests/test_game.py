from game.game import Game
from game.game_state import GameState
from questions.question import Question


def make_q(qid, answer="1/2"):
    return Question(id=qid, prompt="p", options=[], answer=answer)


def test_play_resets_and_scores():
    g = Game(id="g1", questions=[make_q("a", "1/2"), make_q("b", "1/2")])
    g.play()
    assert g.score == 0
    assert g.state == GameState.PLAYING
    assert g.submit_answer("1/2") is True
    assert g.score == 100
    assert g.submit_answer("1/3") is False
    assert g.score == 100
    assert g.correct == 1
    assert g.answered == 2
    assert g.state == GameState.GAME_OVER


def test_view_score_inputs():
    g = Game(id="g1", questions=[make_q("a")])
    g.play()
    assert g.view_score() == 0
    g.submit_answer("1/2")
    assert g.view_score() == 100


def test_percent_and_stars():
    g = Game(id="g1", questions=[make_q("a"), make_q("b")])
    g.play()
    g.submit_answer("1/2")  # correct
    g.submit_answer("1/3")  # wrong -> 50% -> 1 star
    assert g.percent == 50.0
    assert g.stars == 1


def test_game_over_after_last_question():
    g = Game(id="g1", questions=[make_q("a")])
    g.play()
    g.submit_answer("1/2")
    assert g.state == GameState.GAME_OVER
