"""The player-controlled tank: its stats and how it draws itself."""

import math
from typing import TYPE_CHECKING

import pygame

from tankbattle.settings import TANK_START_AMMO, TANK_START_FUEL, TANK_START_HEALTH
from tankbattle.utils.constants import (
    BARREL_COLOR,
    BARREL_LENGTH,
    BLACK,
    TANK_FUEL_COST_PER_FRAME,
    TANK_HEIGHT,
    TANK_MAX_ANGLE,
    TANK_MIN_ANGLE,
    TANK_MOVE_SPEED,
    TANK_POWER_MAX,
    TANK_POWER_MIN,
    TANK_POWER_STEP,
    TANK_ROTATE_SPEED,
    TANK_WIDTH,
)
from tankbattle.utils.helpers import clamp

if TYPE_CHECKING:
    from tankbattle.models.terrain import Terrain


class Tank:
    def __init__(self, player_id: int, x: float, y: float, color: tuple[int, int, int]):
        self.player_id = player_id
        self.color = color

        self.position = (x, y)
        self.angle = 45.0  # degrees, 0 = pointing right, 180 = pointing left
        self.power = 50.0  # percent, used as launch power in Phase 3
        self.health = TANK_START_HEALTH
        self.fuel = TANK_START_FUEL
        self.current_ammo = TANK_START_AMMO
        self.velocity = (0.0, 0.0)

    def move(self, direction: int, terrain: "Terrain") -> None:
        """Shift the tank left/right along the terrain, consuming fuel. direction is -1 or 1."""
        if direction == 0 or self.fuel <= 0:
            return
        x, _ = self.position
        half_width = TANK_WIDTH / 2
        new_x = clamp(x + direction * TANK_MOVE_SPEED, half_width, terrain.width - half_width)
        self.position = (new_x, terrain.height_at(new_x))
        self.fuel = clamp(self.fuel - TANK_FUEL_COST_PER_FRAME, 0, TANK_START_FUEL)

    def rotate_barrel(self, direction: int) -> None:
        """Adjust the cannon angle. direction is -1 or 1."""
        self.angle = clamp(self.angle + direction * TANK_ROTATE_SPEED, TANK_MIN_ANGLE, TANK_MAX_ANGLE)

    def adjust_power(self, direction: int) -> None:
        """Adjust firing power. direction is -1 or 1."""
        self.power = clamp(self.power + direction * TANK_POWER_STEP, TANK_POWER_MIN, TANK_POWER_MAX)

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
