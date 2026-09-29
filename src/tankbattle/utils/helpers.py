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


def distance_to_segment(
    point: tuple[float, float], seg_start: tuple[float, float], seg_end: tuple[float, float]
) -> float:
    """Shortest distance from a point to a line segment."""
    px, py = point
    ax, ay = seg_start
    bx, by = seg_end
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return distance(point, seg_start)
    t = clamp(((px - ax) * dx + (py - ay) * dy) / length_sq, 0.0, 1.0)
    closest = (ax + t * dx, ay + t * dy)
    return distance(point, closest)
