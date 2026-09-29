"""Distance-based damage falloff from an explosion: full damage at the center, none past blast_radius."""

import math
from typing import TYPE_CHECKING

from tankbattle.utils.helpers import distance_to_segment

if TYPE_CHECKING:
    from tankbattle.models.tank import Tank


def distance_to_tank(point: tuple[float, float], tank: "Tank") -> float:
    """Distance from a point to the nearest part of a tank: its body rectangle or its barrel (0 if inside)."""
    body = tank.get_rect()
    dx = max(body.left - point[0], 0, point[0] - body.right)
    dy = max(body.top - point[1], 0, point[1] - body.bottom)
    to_body = math.hypot(dx, dy)
    to_barrel = distance_to_segment(point, body.center, tank.barrel_tip())
    return min(to_body, to_barrel)


def calculate_damage(distance: float, blast_radius: float, max_damage: float) -> float:
    """Damage dealt to a tank at `distance` from the blast center."""
    if blast_radius <= 0 or distance >= blast_radius:
        return 0.0
    falloff = 1 - (distance / blast_radius)
    return max_damage * falloff
