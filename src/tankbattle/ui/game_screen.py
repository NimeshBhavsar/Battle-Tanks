"""Draws one frame in the order: sky, terrain, tanks, projectile, explosion, HUD."""

import pygame

from tankbattle.engine.turn_manager import TurnManager
from tankbattle.models.player import Player
from tankbattle.models.projectile import Projectile
from tankbattle.models.tank import Tank
from tankbattle.models.terrain import Terrain
from tankbattle.ui import hud
from tankbattle.utils.constants import (
    BLACK,
    DAMAGE_POPUP_COLOR,
    DAMAGE_POPUP_RISE,
    EXPLOSION_COLOR,
    EXPLOSION_CORE_COLOR,
    EXPLOSION_RADIUS,
    FUEL_PICKUP_CAP_COLOR,
    FUEL_PICKUP_COLOR,
    FUEL_PICKUP_HEIGHT,
    FUEL_PICKUP_WIDTH,
    SKY_COLOR,
    TANK_HEIGHT,
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
    fuel_pickups: list[tuple[float, float]] | None = None,
    damage_popups: list[tuple[int, int, float]] | None = None,
) -> None:
    """Draw one complete frame onto the surface."""
    surface.fill(SKY_COLOR)
    terrain.draw(surface)
    for pickup in fuel_pickups or []:
        _draw_fuel_pickup(surface, pickup)
    for player in players:
        player.tank.draw(surface)
    if trajectory:
        for point in trajectory:
            pygame.draw.circle(surface, TRAJECTORY_DOT_COLOR, (int(point[0]), int(point[1])), TRAJECTORY_DOT_RADIUS)
    if projectile is not None:
        projectile.draw(surface)
    if explosion is not None:
        _draw_explosion(surface, explosion, explosion_progress)
    tanks_by_id = {player.player_id: player.tank for player in players}
    for player_id, amount, progress in damage_popups or []:
        _draw_damage_popup(surface, font, tanks_by_id[player_id], amount, progress)

    hud.draw_scoreboard(surface, font, players)
    if game_over_text and big_font is not None:
        hud.draw_message(surface, big_font, game_over_text)
        hud.draw_message(surface, font, "Press Esc for the menu to restart", y_offset=60)
    else:
        hud.draw_turn_indicator(surface, font, turn_manager)


def _draw_damage_popup(
    surface: pygame.Surface, font: pygame.font.Font, tank: Tank, amount: int, progress: float
) -> None:
    """Draw "-N HP" in red above the tank, drifting upward and fading out as progress goes from 0 to 1."""
    progress = clamp(progress, 0.0, 1.0)
    label = f"-{amount} HP"
    text = font.render(label, True, DAMAGE_POPUP_COLOR)
    outline = font.render(label, True, BLACK)
    text_surface = pygame.Surface((text.get_width() + 2, text.get_height() + 2), pygame.SRCALPHA)
    for dx, dy in ((0, 1), (2, 1), (1, 0), (1, 2)):
        text_surface.blit(outline, (dx, dy))
    text_surface.blit(text, (1, 1))
    text_surface.set_alpha(int(255 * (1 - progress**2)))

    x, ground_y = tank.position
    bottom = ground_y - TANK_HEIGHT - 24 - DAMAGE_POPUP_RISE * progress  # clear of the barrel and HUD text
    surface.blit(text_surface, text_surface.get_rect(midbottom=(int(x), int(bottom))))


def _draw_fuel_pickup(surface: pygame.Surface, position: tuple[float, float]) -> None:
    """Draw a little jerrycan standing on the ground at `position`."""
    x, y = int(position[0]), int(position[1])
    body = pygame.Rect(0, 0, FUEL_PICKUP_WIDTH, FUEL_PICKUP_HEIGHT)
    body.midbottom = (x, y + 2)  # sink slightly so it sits on the terrain
    pygame.draw.rect(surface, FUEL_PICKUP_COLOR, body, border_radius=2)
    pygame.draw.rect(surface, BLACK, body, width=1, border_radius=2)
    cap = pygame.Rect(0, 0, 6, 4)
    cap.midbottom = (body.centerx + 3, body.top)
    pygame.draw.rect(surface, FUEL_PICKUP_CAP_COLOR, cap)
    pygame.draw.rect(surface, BLACK, cap, width=1)
    pygame.draw.line(surface, FUEL_PICKUP_CAP_COLOR, (body.left + 3, body.centery), (body.right - 3, body.centery), 2)


def _draw_explosion(surface: pygame.Surface, position: tuple[float, float], progress: float) -> None:
    """Fireball core shrinking while a shockwave ring expands outward."""
    progress = clamp(progress, 0.0, 1.0)
    center = (int(position[0]), int(position[1]))

    outer_radius = int(EXPLOSION_RADIUS * (0.4 + 1.4 * progress))
    pygame.draw.circle(surface, EXPLOSION_COLOR, center, max(1, outer_radius), width=3)

    inner_radius = int(EXPLOSION_RADIUS * (1 - progress))
    if inner_radius > 1:
        pygame.draw.circle(surface, EXPLOSION_CORE_COLOR, center, inner_radius)
