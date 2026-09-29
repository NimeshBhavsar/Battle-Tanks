"""Purely visual effects driven by the client: particles (smoke, debris), screen shake and hit flashes.

Nothing here touches game state - the client feeds it events it noticed in the server's
broadcasts (a shell in flight, an explosion, a hit) and it decides how they look.
"""

import math
import random

import pygame

from tankbattle.utils.constants import (
    DEBRIS_COLORS,
    EXPLOSION_SMOKE_COLOR,
    HIT_FLASH_FRAMES,
    MAX_PARTICLES,
    SHAKE_FRAMES,
    SHAKE_PER_BLAST_RADIUS,
    SMOKE_TRAIL_COLOR,
)


class Particle:
    """One short-lived dot: smoke fades and swells, debris falls under gravity."""

    __slots__ = ("x", "y", "vx", "vy", "gravity", "size", "grow", "color", "life", "age", "fade_from")

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        life: int,
        size: float,
        color: tuple[int, int, int],
        gravity: float = 0.0,
        grow: float = 0.0,
        fade_from: float = 0.0,
    ):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = life
        self.age = 0
        self.size = size
        self.grow = grow
        self.color = color
        self.gravity = gravity
        self.fade_from = fade_from  # fraction of the lifetime after which the particle starts fading out

    def update(self) -> None:
        """Advance one frame."""
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.age += 1

    @property
    def alive(self) -> bool:
        """Whether the particle still has life left."""
        return self.age < self.life

    @property
    def alpha(self) -> int:
        """Opacity from 0 to 255, fading out over the last part of its life."""
        t = self.age / self.life
        if t <= self.fade_from:
            return 255
        return int(255 * (1 - (t - self.fade_from) / (1 - self.fade_from)))


class Effects:
    """Owns all active particles, the current screen shake and any tanks that are flashing."""

    def __init__(self):
        self.particles: list[Particle] = []
        self._shake_strength = 0.0
        self._shake_left = 0
        self._flash_age: dict[int, int] = {}

    def add_smoke_trail(self, position: tuple[float, float], weight: float) -> None:
        """Leave a puff of smoke where a shell currently is; heavier shells smoke more."""
        x, y = position
        self._add(
            Particle(
                x + random.uniform(-1, 1),
                y + random.uniform(-1, 1),
                random.uniform(-0.15, 0.15),
                random.uniform(-0.3, -0.05),
                life=random.randint(25, 40),
                size=2 + weight * 0.3,
                grow=0.08,
                color=SMOKE_TRAIL_COLOR,
                fade_from=0.0,
            )
        )

    def add_explosion(self, position: tuple[float, float], blast_radius: float) -> None:
        """Throw up debris and smoke, and shake the screen in proportion to the blast size."""
        x, y = position
        for _ in range(int(blast_radius * 0.7)):
            angle = random.uniform(math.pi * 1.05, math.pi * 1.95)  # upward fan (screen y grows downward)
            speed = random.uniform(2.0, 2.0 + blast_radius * 0.12)
            self._add(
                Particle(
                    x + random.uniform(-blast_radius, blast_radius) * 0.3,
                    y,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    life=random.randint(40, 60),
                    size=random.uniform(1.5, 3.5),
                    color=random.choice(DEBRIS_COLORS),
                    gravity=0.25,
                    fade_from=0.7,
                )
            )
        for _ in range(6 + int(blast_radius // 6)):
            self._add(
                Particle(
                    x + random.uniform(-blast_radius, blast_radius) * 0.4,
                    y + random.uniform(-6, 6),
                    random.uniform(-0.6, 0.6),
                    random.uniform(-1.2, -0.3),
                    life=random.randint(45, 70),
                    size=random.uniform(4, 7),
                    grow=0.15,
                    color=EXPLOSION_SMOKE_COLOR,
                )
            )
        self._shake_strength = max(self._shake_strength, blast_radius * SHAKE_PER_BLAST_RADIUS)
        self._shake_left = SHAKE_FRAMES

    def add_hit_flash(self, player_id: int) -> None:
        """Make a tank flash white."""
        self._flash_age[player_id] = 0

    def update(self) -> None:
        """Advance every effect by one frame."""
        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if p.alive]

        if self._shake_left > 0:
            self._shake_left -= 1
        else:
            self._shake_strength = 0.0

        self._flash_age = {pid: age + 1 for pid, age in self._flash_age.items() if age + 1 < HIT_FLASH_FRAMES}

    def shake_offset(self) -> tuple[int, int]:
        """Return a random (dx, dy) to shift the whole frame by; (0, 0) when nothing is shaking."""
        if self._shake_left <= 0:
            return 0, 0
        strength = self._shake_strength * self._shake_left / SHAKE_FRAMES  # dies down as it goes
        return round(random.uniform(-strength, strength)), round(random.uniform(-strength, strength))

    def flash_progress(self, player_id: int) -> float | None:
        """How far through its white flash a tank is (0 = just hit, 1 = over), or None if it isn't flashing."""
        age = self._flash_age.get(player_id)
        return None if age is None else age / HIT_FLASH_FRAMES

    def draw_particles(self, surface: pygame.Surface) -> None:
        """Draw all particles; translucent ones go through a small alpha surface."""
        for particle in self.particles:
            size = particle.size + particle.grow * particle.age
            alpha = particle.alpha
            center = (int(particle.x), int(particle.y))
            if alpha >= 250:
                pygame.draw.circle(surface, particle.color, center, max(1, round(size)))
                continue
            radius = max(1, round(size))
            dot = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(dot, (*particle.color, max(0, alpha) // 2 + 20), (radius, radius), radius)
            surface.blit(dot, (center[0] - radius, center[1] - radius))

    def _add(self, particle: Particle) -> None:
        if len(self.particles) < MAX_PARTICLES:
            self.particles.append(particle)
