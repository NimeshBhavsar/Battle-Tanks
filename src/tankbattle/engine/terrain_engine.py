"""Turns an explosion into terrain deformation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tankbattle.models.terrain import Terrain


def carve_crater(terrain: "Terrain", x: float, y: float, radius: float) -> None:
    """Apply a crater to the terrain's height map at the explosion point."""
    terrain.destroy_circle(x, y, radius)
