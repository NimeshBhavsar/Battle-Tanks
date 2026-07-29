"""The player-controlled tank: its stats and how it draws itself."""

import math

import pygame

from tankbattle.settings import TANK_START_AMMO, TANK_START_FUEL, TANK_START_HEALTH
from tankbattle.utils.constants import BARREL_COLOR, BARREL_LENGTH, BLACK, TANK_HEIGHT, TANK_WIDTH


class Tank:
    def __init__(self, player_id: int, x: float, y: float, color: tuple[int, int, int]):
        self.player_id = player_id
        self.color = color

        self.position = (x, y)
        self.angle = 45.0  # degrees, 0 = pointing right
        self.health = TANK_START_HEALTH
        self.fuel = TANK_START_FUEL
        self.current_ammo = TANK_START_AMMO
        self.velocity = (0.0, 0.0)

    def move(self, direction: int) -> None:
        """Shift the tank left/right along the terrain. Implemented in Phase 2."""
        raise NotImplementedError("Tank movement lands in Phase 2")

    def rotate_barrel(self, delta_degrees: float) -> None:
        """Adjust the cannon angle. Implemented in Phase 2."""
        raise NotImplementedError("Barrel rotation lands in Phase 2")

    def fire(self):
        """Launch a projectile using the current angle/power/ammo. Implemented in Phase 3."""
        raise NotImplementedError("Firing lands in Phase 3")

    def take_damage(self, amount: float) -> None:
        """Reduce health, floored at zero. Implemented in Phase 4."""
        raise NotImplementedError("Damage handling lands in Phase 4")

    def draw(self, surface: pygame.Surface) -> None:
        x, y = self.position
        body_rect = pygame.Rect(0, 0, TANK_WIDTH, TANK_HEIGHT)
        body_rect.midbottom = (x, y)
        pygame.draw.rect(surface, self.color, body_rect, border_radius=3)
        pygame.draw.rect(surface, BLACK, body_rect, width=1, border_radius=3)

        barrel_origin = body_rect.center
        angle_rad = math.radians(self.angle)
        barrel_end = (
            barrel_origin[0] + BARREL_LENGTH * math.cos(angle_rad),
            barrel_origin[1] - BARREL_LENGTH * math.sin(angle_rad),
        )
        pygame.draw.line(surface, BARREL_COLOR, barrel_origin, barrel_end, 4)
