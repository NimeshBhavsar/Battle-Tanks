"""Destructible terrain, stored as a height map rather than per-pixel data."""

import math
import random

import pygame

from tankbattle.utils.constants import GROUND_COLOR, GROUND_OUTLINE_COLOR, SCREEN_HEIGHT, SCREEN_WIDTH


class Terrain:
    """Destructible terrain stored as one ground height per pixel column."""

    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT, seed: int | None = None):
        self.width = width
        self.height = height
        self.height_map: list[int] = self._generate_height_map(seed)

    def _generate_height_map(self, seed: int | None) -> list[int]:
        """Random-walk + smoothing pass, producing one ground height per pixel column."""
        rng = random.Random(seed)
        base = self.height * 0.6
        raw = [base]
        for _ in range(1, self.width):
            step = rng.uniform(-4, 4)
            next_value = raw[-1] + step
            next_value = max(self.height * 0.35, min(self.height * 0.85, next_value))
            raw.append(next_value)

        smoothed = []
        window = 15
        for x in range(self.width):
            lo = max(0, x - window)
            hi = min(self.width, x + window)
            smoothed.append(int(sum(raw[lo:hi]) / (hi - lo)))
        return smoothed

    def height_at(self, x: int) -> int:
        """Ground surface y-coordinate at pixel column x."""
        x = max(0, min(self.width - 1, int(x)))
        return self.height_map[x]

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the ground as a filled polygon."""
        points = [(0, self.height)]
        points += [(x, self.height_map[x]) for x in range(self.width)]
        points.append((self.width, self.height))
        pygame.draw.polygon(surface, GROUND_COLOR, points)
        pygame.draw.lines(surface, GROUND_OUTLINE_COLOR, False, [(x, self.height_map[x]) for x in range(self.width)], 2)

    def destroy_circle(self, x: float, y: float, radius: float) -> None:
        """Carve a circular crater into the height map, centered at (x, y)."""
        center = int(x)
        left = max(0, center - int(radius))
        right = min(self.width - 1, center + int(radius))
        for col in range(left, right + 1):
            dx = col - x
            if abs(dx) > radius:
                continue
            crater_bottom = y + math.sqrt(radius * radius - dx * dx)
            self.height_map[col] = min(self.height, max(self.height_map[col], int(crater_bottom)))

    def collision(self, x: int, y: int) -> bool:
        """Whether point (x, y) is at or below the ground surface."""
        return y >= self.height_at(x)
