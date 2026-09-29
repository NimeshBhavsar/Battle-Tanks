"""Tank Battle: a networked, turn-based artillery game built with Pygame.

The most useful building blocks are re-exported here, so they can be imported straight
from the package, e.g. ``from tankbattle import Tank, Terrain, GameServer``.
"""

from tankbattle.client import GameClient
from tankbattle.engine.turn_manager import TurnManager
from tankbattle.main import main
from tankbattle.models.ammunition import Ammo, HeavyShell, LightShell, MediumShell
from tankbattle.models.player import Player
from tankbattle.models.projectile import Projectile
from tankbattle.models.tank import Tank
from tankbattle.models.terrain import Terrain
from tankbattle.server import GameServer

__all__ = [
    "Ammo",
    "GameClient",
    "GameServer",
    "HeavyShell",
    "LightShell",
    "MediumShell",
    "Player",
    "Projectile",
    "Tank",
    "Terrain",
    "TurnManager",
    "main",
]
