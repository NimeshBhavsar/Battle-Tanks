"""Heads-up display: a per-player HP/fuel scoreboard, plus the active player's aim."""

import pygame

from tankbattle.engine.turn_manager import TurnManager
from tankbattle.models.player import Player
from tankbattle.settings import TANK_START_FUEL, TANK_START_HEALTH
from tankbattle.utils.constants import (
    BAR_BG_COLOR,
    BAR_GAP,
    BAR_HEIGHT,
    BAR_WIDTH,
    BLACK,
    FUEL_BAR_COLOR,
    HP_BAR_COLOR,
    HUD_TEXT_COLOR,
)
from tankbattle.utils.helpers import clamp


def _draw_bar(surface: pygame.Surface, x: int, y: int, fraction: float, fill_color: tuple[int, int, int]) -> None:
    rect = pygame.Rect(x, y, BAR_WIDTH, BAR_HEIGHT)
    pygame.draw.rect(surface, BAR_BG_COLOR, rect, border_radius=3)
    fill_width = int(BAR_WIDTH * clamp(fraction, 0.0, 1.0))
    if fill_width > 0:
        pygame.draw.rect(surface, fill_color, (x, y, fill_width, BAR_HEIGHT), border_radius=3)
    pygame.draw.rect(surface, BLACK, rect, width=1, border_radius=3)


def _draw_bar_label(
    surface: pygame.Surface,
    font: pygame.font.Font,
    label: str,
    x: int,
    y: int,
    on_left: bool,
    color: tuple[int, int, int],
) -> None:
    """Tag a bar with its name, placed on the side facing the screen center."""
    text = font.render(label, True, color)
    if on_left:
        rect = text.get_rect(midleft=(x + BAR_WIDTH + 6, y + BAR_HEIGHT // 2))
    else:
        rect = text.get_rect(midright=(x - 6, y + BAR_HEIGHT // 2))
    surface.blit(text, rect)


def draw_scoreboard(surface: pygame.Surface, font: pygame.font.Font, players: list[Player]) -> None:
    """Both players' HP and fuel bars, always visible regardless of whose turn it is."""
    label_font = pygame.font.SysFont(None, 18)
    for index, player in enumerate(players):
        tank = player.tank
        x = 12 if index == 0 else surface.get_width() - 12 - BAR_WIDTH

        name_text = font.render(player.name, True, tank.color)
        name_rect = name_text.get_rect(topleft=(x, 12))
        surface.blit(name_text, name_rect)

        hp_y = name_rect.bottom + 4
        _draw_bar(surface, x, hp_y, tank.health / TANK_START_HEALTH, HP_BAR_COLOR)
        _draw_bar_label(surface, label_font, "HP", x, hp_y, index == 0, HP_BAR_COLOR)

        fuel_y = hp_y + BAR_HEIGHT + BAR_GAP
        _draw_bar(surface, x, fuel_y, tank.fuel / TANK_START_FUEL, FUEL_BAR_COLOR)
        _draw_bar_label(surface, label_font, "FUEL", x, fuel_y, index == 0, FUEL_BAR_COLOR)


def draw_turn_indicator(surface: pygame.Surface, font: pygame.font.Font, turn_manager: TurnManager) -> None:
    """Draw the active player's name and aim readout at the top center."""
    tank = turn_manager.current_player.tank
    label = (
        f"{turn_manager.current_player.name}'s Turn"
        f"  —  Angle {int(tank.angle)}°  Power {int(tank.power)}%  Ammo {tank.current_ammo.name} (1/2/3)"
    )
    text = font.render(label, True, HUD_TEXT_COLOR)
    rect = text.get_rect(midtop=(surface.get_width() // 2, 12))
    surface.blit(text, rect)


def draw_message(surface: pygame.Surface, font: pygame.font.Font, message: str, y_offset: int = 0) -> None:
    """Draw a message on a black box at the screen center, shifted down by y_offset."""
    text = font.render(message, True, HUD_TEXT_COLOR)
    rect = text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + y_offset))
    pygame.draw.rect(surface, BLACK, rect.inflate(40, 24), border_radius=8)
    surface.blit(text, rect)
