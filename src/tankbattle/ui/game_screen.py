"""Draws one frame in the order: sky, terrain, tanks, projectile, explosion, HUD."""

import pygame

from tankbattle.engine.turn_manager import TurnManager
from tankbattle.models.player import Player
from tankbattle.models.projectile import Projectile
from tankbattle.models.terrain import Terrain
from tankbattle.ui import hud
from tankbattle.utils.constants import EXPLOSION_COLOR, EXPLOSION_RADIUS, SKY_COLOR


def render(
    surface: pygame.Surface,
    terrain: Terrain,
    players: list[Player],
    turn_manager: TurnManager,
    font: pygame.font.Font,
    projectile: Projectile | None = None,
    explosion: tuple[float, float] | None = None,
) -> None:
    surface.fill(SKY_COLOR)
    terrain.draw(surface)
    for player in players:
        player.tank.draw(surface)
    if projectile is not None:
        projectile.draw(surface)
    if explosion is not None:
        pygame.draw.circle(surface, EXPLOSION_COLOR, (int(explosion[0]), int(explosion[1])), EXPLOSION_RADIUS)
    hud.draw_turn_indicator(surface, font, turn_manager)
