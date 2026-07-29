"""Heads-up display. Phase 1 only renders the turn indicator; health/ammo/power land later."""

import pygame

from tankbattle.engine.turn_manager import TurnManager
from tankbattle.utils.constants import HUD_TEXT_COLOR


def draw_turn_indicator(surface: pygame.Surface, font: pygame.font.Font, turn_manager: TurnManager) -> None:
    text = font.render(f"{turn_manager.current_player.name}'s Turn", True, HUD_TEXT_COLOR)
    rect = text.get_rect(midtop=(surface.get_width() // 2, 12))
    surface.blit(text, rect)
