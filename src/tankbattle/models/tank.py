"""The player-controlled tank: its stats and how it draws itself."""

import math
from typing import TYPE_CHECKING

import pygame

from tankbattle.engine import physics
from tankbattle.models.ammunition import LightShell
from tankbattle.models.projectile import Projectile
from tankbattle.settings import TANK_START_FUEL, TANK_START_HEALTH
from tankbattle.utils.constants import (
    AMMO_WEIGHT_GRAVITY_SCALE,
    BARREL_COLOR,
    BARREL_LENGTH,
    BARREL_THICKNESS,
    BLACK,
    LAUNCH_POWER_SCALE,
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
    TRAJECTORY_MAX_POINTS,
    TRAJECTORY_STEPS_PER_POINT,
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
        self.current_ammo = LightShell()
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

    def fire(self) -> Projectile:
        """Launch a projectile from the barrel tip using the current angle/power/ammo."""
        speed = self.power * LAUNCH_POWER_SCALE
        velocity = physics.launch_velocity(speed, self.angle)
        ammo = self.current_ammo
        return Projectile(
            position=self.barrel_tip(),
            velocity=velocity,
            weight=ammo.weight,
            damage=ammo.damage,
            blast_radius=ammo.blast_radius,
        )

    def preview_trajectory(self, terrain: "Terrain") -> list[tuple[float, float]]:
        """Sample points along the arc this tank would fire along right now, for an aiming aid."""
        position = self.barrel_tip()
        velocity = physics.launch_velocity(self.power * LAUNCH_POWER_SCALE, self.angle)
        weight_factor = self.current_ammo.weight * AMMO_WEIGHT_GRAVITY_SCALE

        points: list[tuple[float, float]] = []
        for i in range(TRAJECTORY_MAX_POINTS * TRAJECTORY_STEPS_PER_POINT):
            position, velocity = physics.step(position, velocity, weight_factor)
            if i % TRAJECTORY_STEPS_PER_POINT == 0:
                points.append(position)
            x, y = position
            if y >= terrain.height_at(x) or x < 0 or x > terrain.width or y > terrain.height:
                break
        return points

    def take_damage(self, amount: float) -> None:
        """Reduce health, floored at zero."""
        self.health = clamp(self.health - amount, 0, TANK_START_HEALTH)

    @property
    def alive(self) -> bool:
        return self.health > 0

    def get_rect(self) -> pygame.Rect:
        rect = pygame.Rect(0, 0, TANK_WIDTH, TANK_HEIGHT)
        rect.midbottom = self.position
        return rect

    def barrel_tip(self) -> tuple[float, float]:
        body_rect = self.get_rect()
        angle_rad = math.radians(self.angle)
        return (
            body_rect.centerx + BARREL_LENGTH * math.cos(angle_rad),
            body_rect.centery - BARREL_LENGTH * math.sin(angle_rad),
        )

    def draw(self, surface: pygame.Surface) -> None:
        body_rect = self.get_rect()
        pygame.draw.rect(surface, self.color, body_rect, border_radius=3)
        pygame.draw.rect(surface, BLACK, body_rect, width=1, border_radius=3)
        pygame.draw.line(surface, BARREL_COLOR, body_rect.center, self.barrel_tip(), BARREL_THICKNESS)
