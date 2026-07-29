"""Draws one frame in the order: sky, terrain, tanks, projectile/explosion, HUD."""

import pygame

from tankbattle.engine.turn_manager import TurnManager
from tankbattle.models.player import Player
from tankbattle.models.terrain import Terrain
from tankbattle.ui import hud
from tankbattle.utils.constants import SKY_COLOR


def render(surface: pygame.Surface, terrain: Terrain, players: list[Player], turn_manager: TurnManager, font: pygame.font.Font) -> None:
    surface.fill(SKY_COLOR)
    terrain.draw(surface)
    for player in players:
        player.tank.draw(surface)
    hud.draw_turn_indicator(surface, font, turn_manager)
