"""Projectile-vs-world collision checks: tanks, terrain, map bounds."""

from typing import TYPE_CHECKING

from tankbattle.utils.constants import BARREL_THICKNESS
from tankbattle.utils.helpers import distance_to_segment

if TYPE_CHECKING:
    from tankbattle.models.projectile import Projectile
    from tankbattle.models.tank import Tank
    from tankbattle.models.terrain import Terrain


def _hits_tank(point: tuple[float, float], tank: "Tank", radius: float) -> bool:
    """Body rect (inflated by the shell's own size) plus a thin band around its barrel."""
    hitbox = tank.get_rect().inflate(radius * 2, radius * 2)
    if hitbox.collidepoint(point):
        return True
    tolerance = BARREL_THICKNESS / 2 + radius
    return distance_to_segment(point, tank.get_rect().center, tank.barrel_tip()) <= tolerance


def check_collision(projectile: "Projectile", terrain: "Terrain", tanks: list["Tank"]) -> tuple[float, float] | None:
    """Return the explosion point once the projectile hits a tank, the ground, or leaves the map."""
    x, y = projectile.position

    for tank in tanks:
        if _hits_tank((x, y), tank, projectile.radius):
            return projectile.position

    if y >= terrain.height_at(x):
        return projectile.position

    if x < 0 or x > terrain.width or y > terrain.height:
        return projectile.position

    return None
