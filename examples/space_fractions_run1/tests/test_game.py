"""Game class tests: scoring, percentage, stars, serialization."""
from game.game import Game
from game.state import GameState


def test_score_starts_zero():
    g = Game()
    assert g.view_score() == 0
    assert g.score == 0


def test_record_answer_increments():
    g = Game()
    g.record_answer(True)
    g.record_answer(False)
    g.record_answer(True)
    assert g.score == 2
    assert g.total == 3


def test_percentage():
    g = Game()
    g.record_answer(True)
    g.record_answer(True)
    g.record_answer(False)
    g.record_answer(True)
    assert g.percentage() == 75.0


def test_stars():
    g = Game()
    g.record_answer(True)
    g.record_answer(False)
    g.record_answer(False)
    assert g.percentage() == 33.33
    assert g.stars() == 0

    g2 = Game()
    for _ in range(6):
        g2.record_answer(True)
    for _ in range(4):
        g2.record_answer(False)
    assert g2.percentage() == 60.0
    assert g2.stars() == 1

    g3 = Game()
    for _ in range(8):
        g3.record_answer(True)
    for _ in range(2):
        g3.record_answer(False)
    assert g3.percentage() == 80.0
    assert g3.stars() == 2

    g4 = Game()
    for _ in range(10):
        g4.record_answer(True)
    assert g4.percentage() == 100.0
    assert g4.stars() == 3


def test_serialization_roundtrip():
    g = Game(game_id="abc")
    g.record_answer(True)
    state = g.to_state()
    g2 = Game.from_state(state)
    assert g2.id == "abc"
    assert g2.score == 1
    assert g2.total == 1
    assert g2.state is GameState.PLAYING
