"""Draws one frame in the order: sky, terrain, tanks, projectile, explosion, HUD."""

import pygame

from tankbattle.engine.turn_manager import TurnManager
from tankbattle.models.player import Player
from tankbattle.models.projectile import Projectile
from tankbattle.models.terrain import Terrain
from tankbattle.ui import hud
from tankbattle.utils.constants import EXPLOSION_COLOR, EXPLOSION_RADIUS, SKY_COLOR, TRAJECTORY_DOT_COLOR, TRAJECTORY_DOT_RADIUS


def render(
    surface: pygame.Surface,
    terrain: Terrain,
    players: list[Player],
    turn_manager: TurnManager,
    font: pygame.font.Font,
    projectile: Projectile | None = None,
    explosion: tuple[float, float] | None = None,
    game_over_text: str | None = None,
    big_font: pygame.font.Font | None = None,
    trajectory: list[tuple[float, float]] | None = None,
) -> None:
    surface.fill(SKY_COLOR)
    terrain.draw(surface)
    for player in players:
        player.tank.draw(surface)
    if trajectory:
        for point in trajectory:
            pygame.draw.circle(surface, TRAJECTORY_DOT_COLOR, (int(point[0]), int(point[1])), TRAJECTORY_DOT_RADIUS)
    if projectile is not None:
        projectile.draw(surface)
    if explosion is not None:
        pygame.draw.circle(surface, EXPLOSION_COLOR, (int(explosion[0]), int(explosion[1])), EXPLOSION_RADIUS)

    if game_over_text and big_font is not None:
        hud.draw_message(surface, big_font, game_over_text)
    else:
        hud.draw_turn_indicator(surface, font, turn_manager)
