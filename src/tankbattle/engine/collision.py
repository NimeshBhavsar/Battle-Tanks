"""Projectile-vs-world collision checks: tanks, terrain, map bounds."""

from typing import TYPE_CHECKING

from tankbattle.utils.constants import BARREL_THICKNESS, PROJECTILE_RADIUS
from tankbattle.utils.helpers import distance_to_segment

if TYPE_CHECKING:
    from tankbattle.models.projectile import Projectile
    from tankbattle.models.tank import Tank
    from tankbattle.models.terrain import Terrain

_BARREL_HIT_TOLERANCE = BARREL_THICKNESS / 2 + PROJECTILE_RADIUS


def _hits_tank(point: tuple[float, float], tank: "Tank") -> bool:
    """Pixel-accurate-ish hit test: the tank's body rect, plus a thin band around its barrel."""
    if tank.get_rect().collidepoint(point):
        return True
    return distance_to_segment(point, tank.get_rect().center, tank.barrel_tip()) <= _BARREL_HIT_TOLERANCE


def check_collision(projectile: "Projectile", terrain: "Terrain", tanks: list["Tank"]) -> tuple[float, float] | None:
    """Return the explosion point once the projectile hits a tank, the ground, or leaves the map."""
    x, y = projectile.position

    for tank in tanks:
        if _hits_tank((x, y), tank):
            return projectile.position

    if y >= terrain.height_at(x):
        return projectile.position

    if x < 0 or x > terrain.width or y > terrain.height:
        return projectile.position

    return None
