"""Shared fixtures. Pygame is told to use dummy video/audio drivers so the tests need no display."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import time  # noqa: E402

import pytest  # noqa: E402

import tankbattle.server as server_module  # noqa: E402
from tankbattle.engine.turn_manager import TurnManager  # noqa: E402
from tankbattle.models.tank import Tank  # noqa: E402
from tankbattle.models.terrain import Terrain  # noqa: E402
from tankbattle.server import GameServer, build_players  # noqa: E402

GROUND_Y = 400


@pytest.fixture
def flat_terrain() -> Terrain:
    """Terrain whose ground is a flat line at y=400, so positions in tests are easy to reason about."""
    terrain = Terrain(seed=1)
    terrain.height_map = [GROUND_Y] * terrain.width
    return terrain


@pytest.fixture
def tank(flat_terrain) -> Tank:
    """A tank standing in the middle of the flat terrain (body spans x 480-520, y 380-400)."""
    return Tank(player_id=1, x=500, y=flat_terrain.height_at(500), color=(200, 60, 60))


@pytest.fixture
def server(flat_terrain, monkeypatch, tmp_path) -> GameServer:
    """A GameServer with no sockets, flat terrain, no fuel cans, and stats written to a temp folder."""
    monkeypatch.setattr(server_module, "STATS_DIR", str(tmp_path))
    monkeypatch.setattr(server_module.report, "build_report", lambda match: b"fake-png")  # skip slow matplotlib
    game = GameServer("127.0.0.1", 0)
    game.terrain = flat_terrain
    game.players = build_players(flat_terrain)
    game.turn_manager = TurnManager(game.players)
    game.fuel_pickups = []
    return game


def wait_for(condition, timeout: float = 5.0) -> bool:
    """Poll until condition() is true; used for the server's background chart thread."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if condition():
            return True
        time.sleep(0.02)
    return condition()
