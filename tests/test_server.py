import base64
import json
import random
import socket

import pytest
from conftest import GROUND_Y, wait_for

from tankbattle import network
from tankbattle.models.projectile import Projectile
from tankbattle.server import build_players
from tankbattle.settings import TANK_START_FUEL, TANK_START_HEALTH
from tankbattle.utils.constants import (
    FUEL_PICKUP_MAX,
    FUEL_PICKUP_MIN_TANK_DISTANCE,
    FUEL_PICKUP_REFILL,
    FUEL_PICKUP_START,
    MAX_NAME_LENGTH,
    SCREEN_WIDTH,
)


def fire_at(server, position, weight=1, damage=30, blast=20):
    """Put a live shell at a position and let the server resolve its impact."""
    shooter = server.turn_manager.current_player.tank
    server.active_projectile = Projectile(position, (0, 0), weight, damage, blast)
    server.recorder.start_shot(shooter.player_id, "Light", shooter.angle, shooter.power)
    server._advance_projectile(shooter)


def opponent_of(server):
    return next(p for p in server.players if p is not server.turn_manager.current_player)


class TestSetup:
    def test_two_players_on_opposite_sides(self, flat_terrain):
        p1, p2 = build_players(flat_terrain)
        assert (p1.player_id, p2.player_id) == (1, 2)
        assert p1.tank.position[0] < SCREEN_WIDTH / 2 < p2.tank.position[0]
        assert p1.tank.position[1] == GROUND_Y

    def test_a_new_server_starts_with_the_configured_fuel_cans(self, monkeypatch):
        from tankbattle.server import GameServer

        assert len(GameServer("127.0.0.1", 0).fuel_pickups) == FUEL_PICKUP_START


class TestFuelCans:
    def test_driving_over_a_can_refuels_and_removes_it(self, server):
        tank = server.players[0].tank
        tank.fuel = 10
        server.fuel_pickups = [tank.position[0] + 5]
        server._collect_fuel_pickups(tank)
        assert tank.fuel == 10 + FUEL_PICKUP_REFILL
        assert server.fuel_pickups == []

    def test_fuel_is_capped_at_the_tank_size(self, server):
        tank = server.players[0].tank
        tank.fuel = TANK_START_FUEL - 5
        server.fuel_pickups = [tank.position[0]]
        server._collect_fuel_pickups(tank)
        assert tank.fuel == TANK_START_FUEL

    def test_a_distant_can_is_left_alone(self, server):
        tank = server.players[0].tank
        tank.fuel = 10
        server.fuel_pickups = [tank.position[0] + 300]
        server._collect_fuel_pickups(tank)
        assert tank.fuel == 10 and len(server.fuel_pickups) == 1

    def test_two_cans_at_once_both_count(self, server):
        tank = server.players[0].tank
        tank.fuel = 0
        server.fuel_pickups = [tank.position[0], tank.position[0] + 2]
        server._collect_fuel_pickups(tank)
        assert tank.fuel == 2 * FUEL_PICKUP_REFILL

    def test_ending_turns_adds_cans_up_to_the_maximum(self, server):
        for _ in range(FUEL_PICKUP_MAX + 5):
            server._end_turn()
        assert len(server.fuel_pickups) == FUEL_PICKUP_MAX

    def test_cans_spawn_away_from_tanks_and_each_other(self, server):
        random.seed(0)
        for _ in range(FUEL_PICKUP_MAX):
            server._spawn_fuel_pickup()
        tank_xs = [p.tank.position[0] for p in server.players]
        for i, x in enumerate(server.fuel_pickups):
            assert all(abs(x - tx) >= FUEL_PICKUP_MIN_TANK_DISTANCE for tx in tank_xs)
            assert all(abs(x - other) >= FUEL_PICKUP_MIN_TANK_DISTANCE for other in server.fuel_pickups[:i])

    def test_a_can_follows_the_terrain_in_the_snapshot(self, server):
        server.fuel_pickups = [300.0]
        assert server._snapshot()["fuel_pickups"] == [[300.0, GROUND_Y]]
        server.terrain.height_map[300] = 450  # a crater lowers the ground under it
        assert server._snapshot()["fuel_pickups"] == [[300.0, 450]]

    def test_moving_over_a_can_through_the_input_path(self, server):
        tank = server.players[0].tank
        tank.fuel = 20
        server.fuel_pickups = [tank.position[0] + 4]
        server._apply_input(tank, {"move": 1})
        assert tank.fuel > 20  # burned 0.5, gained 40


class TestTurns:
    def test_moving_then_releasing_the_key_ends_the_turn(self, server):
        tank = server.players[0].tank
        server._apply_input(tank, {"move": 1})
        assert server.turn_manager.current_player.player_id == 1  # still moving
        server._apply_input(tank, {"move": 0})
        assert server.turn_manager.current_player.player_id == 2

    def test_cannot_fire_after_moving(self, server):
        # Regression test: this used to fail - the turn ended, but the same input still fired the old tank's shell.
        tank = server.players[0].tank
        server._apply_input(tank, {"move": 1})
        server._apply_input(tank, {"move": 0, "fire": True})  # released the key and pressed fire in the same frame
        assert server.active_projectile is None
        assert server.turn_manager.current_player.player_id == 2  # the move ended the turn

    def test_firing_creates_a_shell_and_records_it(self, server):
        tank = server.players[0].tank
        server._apply_input(tank, {"fire": True})
        assert server.active_projectile is not None
        assert server.recorder._open_shot["player_id"] == 1

    def test_only_one_shot_per_turn(self, server):
        tank = server.players[0].tank
        server._apply_input(tank, {"fire": True})
        first = server.active_projectile
        server._apply_input(tank, {"fire": True})
        assert server.active_projectile is first

    def test_ammo_can_be_switched_before_firing(self, server):
        tank = server.players[0].tank
        server._apply_input(tank, {"ammo": "Heavy"})
        assert tank.current_ammo.name == "Heavy"
        server._apply_input(tank, {"ammo": "Bogus"})  # unknown names are ignored
        assert tank.current_ammo.name == "Heavy"

    def test_aiming_inputs_change_angle_and_power(self, server):
        tank = server.players[0].tank
        angle, power = tank.angle, tank.power
        server._apply_input(tank, {"rotate": 1, "power": 1})
        assert tank.angle > angle and tank.power > power


class TestImpact:
    def test_a_direct_hit_damages_the_opponent_and_ends_the_turn(self, server):
        target = opponent_of(server)
        fire_at(server, target.tank.get_rect().center)
        assert target.tank.health == TANK_START_HEALTH - 30
        assert server.turn_manager.current_player.player_id == 2
        assert server.active_projectile is None

    def test_a_hit_is_logged_and_announced_to_clients(self, server):
        target = opponent_of(server)
        fire_at(server, target.tank.get_rect().center)
        shot = server.recorder.shots[0]
        assert shot["hit"] and shot["damage_dealt"] == 30
        event = server.damage_events[-1]
        assert (event["player_id"], event["amount"]) == (2, 30)

    def test_each_damage_event_gets_a_new_id(self, server):
        fire_at(server, opponent_of(server).tank.get_rect().center)
        server.acted_this_turn = False
        fire_at(server, opponent_of(server).tank.get_rect().center)
        ids = [e["id"] for e in server.damage_events]
        assert ids == sorted(set(ids)) and len(ids) == 2

    def test_a_miss_does_no_damage_and_passes_the_turn(self, server):
        fire_at(server, (500, GROUND_Y + 5))  # lands in the ground, far from both tanks
        assert all(p.tank.health == TANK_START_HEALTH for p in server.players)
        assert server.recorder.shots[0]["hit"] is False
        assert server.damage_events == []
        assert server.turn_manager.current_player.player_id == 2

    def test_a_crater_is_carved(self, server):
        fire_at(server, (500, GROUND_Y + 5))
        assert server.terrain.height_at(500) > GROUND_Y

    def test_tanks_settle_into_a_crater(self, server):
        tank = server.players[0].tank
        x = tank.position[0]
        fire_at(server, (x, GROUND_Y + 5))
        assert tank.position[1] == server.terrain.height_at(x) > GROUND_Y

    def test_your_own_shell_can_hurt_you_and_is_not_counted_as_a_hit(self, server):
        shooter = server.players[0].tank
        fire_at(server, (shooter.position[0], GROUND_Y + 5))
        assert shooter.health < TANK_START_HEALTH
        assert server.recorder.shots[0]["hit"] is False
        assert server.recorder.shots[0]["damage"]["1"] > 0

    def test_explosion_details_are_published(self, server):
        fire_at(server, (500, GROUND_Y + 5), blast=35)
        snapshot = server._snapshot()
        assert snapshot["explosion"] is not None and snapshot["explosion_radius"] == 35


class TestGameOver:
    def kill_opponent(self, server):
        opponent_of(server).tank.health = 10
        fire_at(server, opponent_of(server).tank.get_rect().center)

    def test_the_last_tank_standing_wins(self, server):
        self.kill_opponent(server)
        assert server.game_over_text == "Player 1 Wins!"

    def test_the_turn_does_not_advance_after_the_match_ends(self, server):
        self.kill_opponent(server)
        assert server.turn_manager.current_player.player_id == 1

    def test_both_tanks_destroyed_is_a_draw(self, server):
        for player in server.players:
            player.tank.health = 5
        server.players[1].tank.position = (server.players[0].tank.position[0] + 10, GROUND_Y)
        fire_at(server, server.players[1].tank.get_rect().center, blast=60)
        assert server.game_over_text == "Draw!"

    def test_finishing_a_match_saves_json_and_the_chart(self, server, tmp_path):
        self.kill_opponent(server)
        assert wait_for(lambda: server._pending_report is not None)
        json_files = list(tmp_path.glob("*.json"))
        assert len(json_files) == 1
        saved = json.loads(json_files[0].read_text())
        assert saved["winner_id"] == 1 and len(saved["shots"]) == 1
        assert json_files[0].with_suffix(".png").read_bytes() == b"fake-png"

    def test_a_chart_failure_does_not_crash_the_server(self, server, monkeypatch, capsys):
        import tankbattle.server as server_module

        def boom(match):
            raise RuntimeError("matplotlib exploded")

        monkeypatch.setattr(server_module.report, "build_report", boom)
        self.kill_opponent(server)
        seen = []
        assert wait_for(lambda: seen.append(capsys.readouterr().out) or "Could not build match report" in "".join(seen))
        assert server._pending_report is None
        assert server.game_over_text is not None

    def test_an_unwritable_stats_folder_does_not_crash_the_server(self, server, monkeypatch, tmp_path):
        import tankbattle.server as server_module

        blocker = tmp_path / "file.txt"
        blocker.write_text("i am a file, not a folder")
        monkeypatch.setattr(server_module, "STATS_DIR", str(blocker / "stats"))
        self.kill_opponent(server)
        assert server.game_over_text is not None


class TestRestart:
    def test_restart_resets_everything(self, server):
        fire_at(server, opponent_of(server).tank.get_rect().center)
        server.game_over_text = "Player 1 Wins!"
        number = server._match_number
        server._reset_match()
        assert server.game_over_text is None
        assert all(p.tank.health == TANK_START_HEALTH for p in server.players)
        assert server.recorder.shots == []
        assert server._match_number == number + 1
        assert len(server.fuel_pickups) == FUEL_PICKUP_START
        assert server.turn_manager.current_player.player_id == 1

    def test_a_chart_from_the_previous_match_is_discarded(self, server):
        old_number = server._match_number
        server._reset_match()
        server._build_report({"anything": 1}, None, old_number)  # a slow chart arriving after a restart
        assert server._pending_report is None


class TestNames:
    def test_a_rename_is_applied_and_consumed(self, server):
        server.pending_inputs = {2: {"name": "Bob"}}
        server._apply_name_changes_locked()
        assert server.players[1].name == "Bob"
        assert server.pending_inputs[2]["name"] is None

    def test_names_are_trimmed_and_length_limited(self, server):
        server.pending_inputs = {1: {"name": "   " + "x" * 50 + "   "}}
        server._apply_name_changes_locked()
        assert server.players[0].name == "x" * MAX_NAME_LENGTH

    def test_a_blank_name_is_ignored(self, server):
        server.pending_inputs = {1: {"name": "     "}}
        server._apply_name_changes_locked()
        assert server.players[0].name == "Player 1"

    def test_renaming_works_on_the_other_players_turn(self, server):
        assert server.turn_manager.current_player.player_id == 1
        server.pending_inputs = {2: {"name": "Zed"}}
        server._apply_name_changes_locked()
        assert server.players[1].name == "Zed"


class TestBroadcast:
    @pytest.fixture
    def wire(self, server):
        server_end, client_end = socket.socketpair()
        client_end.settimeout(1)
        server.client_sockets = {1: server_end}
        yield client_end
        server_end.close()
        client_end.close()

    def test_snapshot_is_json_serializable_and_complete(self, server):
        snapshot = json.loads(json.dumps(server._snapshot()))
        expected = {
            "type", "terrain", "tanks", "current_player_id", "projectile", "explosion", "explosion_radius",
            "fuel_pickups", "damage_events", "game_over_text",
        }
        assert expected <= set(snapshot)
        assert len(snapshot["tanks"]) == 2 and len(snapshot["terrain"]) == SCREEN_WIDTH

    def test_the_report_is_sent_once_after_the_state(self, server, wire):
        server._pending_report = b"chart-bytes"
        server._broadcast_state()
        assert network.receive_message(wire)["type"] == "state"
        report = network.receive_message(wire)
        assert report["type"] == "report" and base64.b64decode(report["png"]) == b"chart-bytes"

        server._broadcast_state()  # the next tick must not resend the chart
        assert network.receive_message(wire)["type"] == "state"
        with pytest.raises(TimeoutError):
            wire.settimeout(0.2)
            network.receive_message(wire)

    def test_a_disconnected_client_is_dropped(self, server):
        server_end, client_end = socket.socketpair()
        server.client_sockets = {1: server_end}
        client_end.close()
        server_end.close()  # sending on it now raises OSError
        server._broadcast_state()
        assert 1 not in server.client_sockets
