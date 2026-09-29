import pygame
import pytest

import tankbattle
from tankbattle.client import GameClient
from tankbattle.ui import report_view
from tankbattle.utils.constants import DAMAGE_POPUP_FRAMES


def event(event_id, player_id=2, amount=30):
    return {"id": event_id, "player_id": player_id, "amount": amount}


@pytest.fixture
def client():
    return GameClient("127.0.0.1", 0)


class TestDamagePopups:
    def test_hits_from_before_we_joined_are_not_replayed(self, client):
        client._update_damage_popups([event(1), event(2)])
        assert client._damage_popups == []

    def test_a_new_hit_creates_a_popup_and_a_flash(self, client):
        client._update_damage_popups([event(1)])
        client._update_damage_popups([event(1), event(2, player_id=2, amount=25)])
        assert len(client._damage_popups) == 1
        assert client._damage_popups[0]["amount"] == 25
        assert client.effects.flash_progress(2) is not None

    def test_the_same_event_is_not_shown_twice(self, client):
        client._update_damage_popups([])
        for _ in range(5):  # the server keeps sending the recent events every tick
            client._update_damage_popups([event(1)])
        assert len(client._damage_popups) == 1

    def test_two_hits_in_one_shot_give_two_popups(self, client):
        client._update_damage_popups([])
        client._update_damage_popups([event(1, player_id=1), event(2, player_id=2)])
        assert {p["player_id"] for p in client._damage_popups} == {1, 2}

    def test_popups_age_and_then_disappear(self, client):
        client._update_damage_popups([])
        client._update_damage_popups([event(1)])
        assert client._damage_popups[0]["age"] == 0
        client._update_damage_popups([event(1)])
        assert client._damage_popups[0]["age"] == 1
        for _ in range(DAMAGE_POPUP_FRAMES):
            client._update_damage_popups([event(1)])
        assert client._damage_popups == []


class TestPlayerStateMirroring:
    def test_a_rename_from_the_server_shows_up_locally(self, client):
        state = {
            "terrain": [400] * 1024,
            "tanks": [
                {"player_id": pid, "name": f"P{pid}", "position": [100 * pid, 400], "angle": 45, "power": 50,
                 "health": 100, "fuel": 100, "ammo": "Light", "color": [1, 2, 3]}
                for pid in (1, 2)
            ],
            "current_player_id": 1,
        }
        client._apply_state(state)
        state["tanks"][0]["name"] = "Alice"
        client._apply_state(state)
        assert next(p for p in client.players if p.player_id == 1).name == "Alice"
        assert len(client.players) == 2  # renaming must not create duplicate players


class TestReportView:
    def test_a_chart_png_becomes_a_surface(self, tmp_path):
        from tankbattle.models.terrain import Terrain
        from tankbattle.report import build_report
        from tankbattle.server import build_players
        from tankbattle.stats import MatchRecorder

        terrain = Terrain(seed=1)
        pygame.display.set_mode((1, 1))  # convert() needs a display (the dummy driver is fine)
        png = build_report(MatchRecorder().finish(build_players(terrain), None))
        chart = report_view.load_chart(png)
        assert chart.get_width() > 100 and chart.get_height() > 100

    def test_the_overlay_draws_with_and_without_a_chart(self):
        pygame.font.init()
        font = pygame.font.SysFont(None, 28)
        surface = pygame.Surface((1024, 576))
        report_view.draw(surface, None, font, font, "Alice Wins!")  # still waiting for the chart
        report_view.draw(surface, pygame.Surface((960, 360)), font, font, "Alice Wins!")

    def test_a_chart_wider_than_the_window_is_shrunk(self):
        pygame.font.init()
        font = pygame.font.SysFont(None, 28)
        report_view.draw(pygame.Surface((400, 300)), pygame.Surface((960, 360)), font, font, "x")


class TestPackageExports:
    @pytest.mark.parametrize("name", tankbattle.__all__)
    def test_everything_advertised_can_be_imported(self, name):
        assert hasattr(tankbattle, name)

    def test_the_readme_example_works(self):
        from tankbattle import HeavyShell, Tank, Terrain

        terrain = Terrain(seed=1)
        tank = Tank(player_id=1, x=200, y=terrain.height_at(200), color=(200, 60, 60))
        tank.current_ammo = HeavyShell()
        assert tank.fire().weight == 6
