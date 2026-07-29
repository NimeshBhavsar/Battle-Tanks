"""Heads-up display: a per-player HP/fuel scoreboard, plus the active player's aim."""

import pygame

from tankbattle.engine.turn_manager import TurnManager
from tankbattle.models.player import Player
from tankbattle.utils.constants import BLACK, HUD_TEXT_COLOR


def draw_scoreboard(surface: pygame.Surface, font: pygame.font.Font, players: list[Player]) -> None:
    """Both players' HP and fuel, always visible regardless of whose turn it is."""
    for index, player in enumerate(players):
        tank = player.tank
        label = f"{player.name}  HP {int(tank.health)}  Fuel {int(tank.fuel)}"
        text = font.render(label, True, tank.color)
        if index == 0:
            rect = text.get_rect(topleft=(12, 12))
        else:
            rect = text.get_rect(topright=(surface.get_width() - 12, 12))
        surface.blit(text, rect)


def draw_turn_indicator(surface: pygame.Surface, font: pygame.font.Font, turn_manager: TurnManager) -> None:
    tank = turn_manager.current_player.tank
    label = (
        f"{turn_manager.current_player.name}'s Turn"
        f"  —  Angle {int(tank.angle)}°  Power {int(tank.power)}%  Ammo {tank.current_ammo.name} (1/2/3)"
    )
    text = font.render(label, True, HUD_TEXT_COLOR)
    rect = text.get_rect(midtop=(surface.get_width() // 2, 12))
    surface.blit(text, rect)


def draw_message(surface: pygame.Surface, font: pygame.font.Font, message: str) -> None:
    text = font.render(message, True, HUD_TEXT_COLOR)
    rect = text.get_rect(center=surface.get_rect().center)
    pygame.draw.rect(surface, BLACK, rect.inflate(40, 24), border_radius=8)
    surface.blit(text, rect)
