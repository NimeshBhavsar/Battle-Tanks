"""Heads-up display. Shows the turn indicator plus the current tank's aim; health/ammo land later."""

import pygame

from tankbattle.engine.turn_manager import TurnManager
from tankbattle.utils.constants import BLACK, HUD_TEXT_COLOR


def draw_turn_indicator(surface: pygame.Surface, font: pygame.font.Font, turn_manager: TurnManager) -> None:
    tank = turn_manager.current_player.tank
    label = (
        f"{turn_manager.current_player.name}'s Turn"
        f"  —  HP {int(tank.health)}  Angle {int(tank.angle)}°  Power {int(tank.power)}%"
        f"  Fuel {int(tank.fuel)}  Ammo {tank.current_ammo.name} (1/2/3)"
    )
    text = font.render(label, True, HUD_TEXT_COLOR)
    rect = text.get_rect(midtop=(surface.get_width() // 2, 12))
    surface.blit(text, rect)


def draw_message(surface: pygame.Surface, font: pygame.font.Font, message: str) -> None:
    text = font.render(message, True, HUD_TEXT_COLOR)
    rect = text.get_rect(center=surface.get_rect().center)
    pygame.draw.rect(surface, BLACK, rect.inflate(40, 24), border_radius=8)
    surface.blit(text, rect)
