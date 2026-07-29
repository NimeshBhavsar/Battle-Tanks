"""Projectile-vs-world collision checks: tanks, terrain, map bounds."""

from typing import TYPE_CHECKING

from tankbattle.utils.constants import PROJECTILE_RADIUS

if TYPE_CHECKING:
    from tankbattle.models.projectile import Projectile
    from tankbattle.models.tank import Tank
    from tankbattle.models.terrain import Terrain


def check_collision(projectile: "Projectile", terrain: "Terrain", tanks: list["Tank"]) -> tuple[float, float] | None:
    """Return the explosion point once the projectile hits a tank, the ground, or leaves the map."""
    x, y = projectile.position

    for tank in tanks:
        hitbox = tank.get_rect().inflate(PROJECTILE_RADIUS * 2, PROJECTILE_RADIUS * 2)
        if hitbox.collidepoint(x, y):
            return projectile.position

    if y >= terrain.height_at(x):
        return projectile.position

    if x < 0 or x > terrain.width or y > terrain.height:
        return projectile.position

    return None
