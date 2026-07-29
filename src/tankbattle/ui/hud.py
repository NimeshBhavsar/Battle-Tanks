"""Heads-up display. Shows the turn indicator plus the current tank's aim; health/ammo land later."""

import pygame

from tankbattle.engine.turn_manager import TurnManager
from tankbattle.utils.constants import HUD_TEXT_COLOR


def draw_turn_indicator(surface: pygame.Surface, font: pygame.font.Font, turn_manager: TurnManager) -> None:
    tank = turn_manager.current_player.tank
    label = (
        f"{turn_manager.current_player.name}'s Turn"
        f"  —  Angle {int(tank.angle)}°  Power {int(tank.power)}%  Fuel {int(tank.fuel)}"
    )
    text = font.render(label, True, HUD_TEXT_COLOR)
    rect = text.get_rect(midtop=(surface.get_width() // 2, 12))
    surface.blit(text, rect)
