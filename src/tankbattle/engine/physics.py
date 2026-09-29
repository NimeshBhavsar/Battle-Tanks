"""Pure projectile kinematics. Knows nothing about tanks; wired up in Phase 3."""

import math

GRAVITY_CONSTANT = 9.8


def launch_velocity(power: float, angle_degrees: float) -> tuple[float, float]:
    """Decompose power + angle into initial (vx, vy).

    Screen y grows downward, so "up" (angle 90) yields a negative vy.
    """
    angle_rad = math.radians(angle_degrees)
    vx = power * math.cos(angle_rad)
    vy = -power * math.sin(angle_rad)
    return vx, vy


def step(
    position: tuple[float, float], velocity: tuple[float, float], weight_factor: float
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Advance one frame: move by velocity, then apply gravity scaled by shell weight."""
    x, y = position
    vx, vy = velocity
    x += vx
    y += vy
    vy += GRAVITY_CONSTANT * weight_factor
    return (x, y), (vx, vy)
