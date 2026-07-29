"""A fired shell in flight."""

import pygame

from tankbattle.engine import physics
from tankbattle.utils.constants import (
    AMMO_WEIGHT_GRAVITY_SCALE,
    PROJECTILE_COLOR,
    PROJECTILE_RADIUS_MIN,
    PROJECTILE_RADIUS_PER_WEIGHT,
)


class Projectile:
    def __init__(self, position: tuple[float, float], velocity: tuple[float, float], weight: float, damage: float, blast_radius: float):
        self.position = position
        self.velocity = velocity
        self.weight = weight
        self.damage = damage
        self.blast_radius = blast_radius
        self.exploded = False

    @property
    def radius(self) -> int:
        """Ball size scales with ammo weight — heavy shells draw (and hit) bigger."""
        return round(PROJECTILE_RADIUS_MIN + self.weight * PROJECTILE_RADIUS_PER_WEIGHT)

    def update(self) -> None:
        """Advance position by one simulation frame."""
        weight_factor = self.weight * AMMO_WEIGHT_GRAVITY_SCALE
        self.position, self.velocity = physics.step(self.position, self.velocity, weight_factor)

    def explode(self) -> tuple[float, float]:
        """Mark this shell as spent and report where it detonated."""
        self.exploded = True
        return self.position

    def draw(self, surface: pygame.Surface) -> None:
        pos = (int(self.position[0]), int(self.position[1]))
        pygame.draw.circle(surface, PROJECTILE_COLOR, pos, self.radius)
