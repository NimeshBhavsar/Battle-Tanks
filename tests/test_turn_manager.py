import pytest

from tankbattle.engine.turn_manager import TurnManager
from tankbattle.models.player import Player
from tankbattle.models.tank import Tank


def make_players(count=2):
    return [Player(i, f"P{i}", Tank(i, 100 * i, 400, (0, 0, 0))) for i in range(1, count + 1)]


def test_first_player_goes_first():
    players = make_players()
    assert TurnManager(players).current_player is players[0]


def test_turns_alternate():
    players = make_players()
    manager = TurnManager(players)
    manager.end_turn()
    assert manager.current_player is players[1]
    manager.end_turn()
    assert manager.current_player is players[0]


def test_it_wraps_around_with_more_players():
    players = make_players(3)
    manager = TurnManager(players)
    for _ in range(3):
        manager.end_turn()
    assert manager.current_player is players[0]


def test_no_players_is_an_error():
    with pytest.raises(ValueError):
        TurnManager([])


def test_set_current_syncs_to_a_player_id():
    players = make_players()
    manager = TurnManager(players)
    manager.set_current(2)
    assert manager.current_player.player_id == 2


def test_set_current_with_an_unknown_id_changes_nothing():
    manager = TurnManager(make_players())
    manager.set_current(99)
    assert manager.current_player.player_id == 1
