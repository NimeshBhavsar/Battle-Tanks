"""Small, generic helper functions used across multiple modules."""

import math


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Restrict value to the inclusive [minimum, maximum] range."""
    return max(minimum, min(value, maximum))


def distance(point_a: tuple[float, float], point_b: tuple[float, float]) -> float:
    """Euclidean distance between two (x, y) points."""
    ax, ay = point_a
    bx, by = point_b
    return math.hypot(bx - ax, by - ay)
