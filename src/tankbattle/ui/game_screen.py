"""Draws one frame in the order: sky, terrain, tanks, projectile, explosion, HUD."""

import pygame

from tankbattle.engine.turn_manager import TurnManager
from tankbattle.models.player import Player
from tankbattle.models.projectile import Projectile
from tankbattle.models.terrain import Terrain
from tankbattle.ui import hud
from tankbattle.utils.constants import (
    EXPLOSION_COLOR,
    EXPLOSION_CORE_COLOR,
    EXPLOSION_RADIUS,
    SKY_COLOR,
    TRAJECTORY_DOT_COLOR,
    TRAJECTORY_DOT_RADIUS,
)
from tankbattle.utils.helpers import clamp


def render(
    surface: pygame.Surface,
    terrain: Terrain,
    players: list[Player],
    turn_manager: TurnManager,
    font: pygame.font.Font,
    projectile: Projectile | None = None,
    explosion: tuple[float, float] | None = None,
    explosion_progress: float = 0.0,
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
        _draw_explosion(surface, explosion, explosion_progress)

    hud.draw_scoreboard(surface, font, players)
    if game_over_text and big_font is not None:
        hud.draw_message(surface, big_font, game_over_text)
        hud.draw_message(surface, font, "Press Esc for the menu to restart", y_offset=60)
    else:
        hud.draw_turn_indicator(surface, font, turn_manager)


def _draw_explosion(surface: pygame.Surface, position: tuple[float, float], progress: float) -> None:
    """Fireball core shrinking while a shockwave ring expands outward."""
    progress = clamp(progress, 0.0, 1.0)
    center = (int(position[0]), int(position[1]))

    outer_radius = int(EXPLOSION_RADIUS * (0.4 + 1.4 * progress))
    pygame.draw.circle(surface, EXPLOSION_COLOR, center, max(1, outer_radius), width=3)

    inner_radius = int(EXPLOSION_RADIUS * (1 - progress))
    if inner_radius > 1:
        pygame.draw.circle(surface, EXPLOSION_CORE_COLOR, center, inner_radius)
