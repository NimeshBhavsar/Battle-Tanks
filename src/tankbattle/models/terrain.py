"""Destructible terrain, stored as a height map rather than per-pixel data."""

import random

import pygame

from tankbattle.utils.constants import GROUND_COLOR, GROUND_OUTLINE_COLOR, SCREEN_HEIGHT, SCREEN_WIDTH


class Terrain:
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
        points = [(0, self.height)]
        points += [(x, self.height_map[x]) for x in range(self.width)]
        points.append((self.width, self.height))
        pygame.draw.polygon(surface, GROUND_COLOR, points)
        pygame.draw.lines(surface, GROUND_OUTLINE_COLOR, False, [(x, self.height_map[x]) for x in range(self.width)], 2)

    def destroy_circle(self, x: int, y: int, radius: int) -> None:
        """Carve a crater into the height map. Implemented in Phase 5."""
        raise NotImplementedError("Terrain deformation lands in Phase 5")

    def collision(self, x: int, y: int) -> bool:
        """Whether point (x, y) is at or below the ground surface. Implemented in Phase 4."""
        raise NotImplementedError("Terrain collision lands in Phase 4")
