"""A fired shell in flight. Implemented in Phase 3."""


class Projectile:
    def __init__(self, position: tuple[float, float], velocity: tuple[float, float], weight: float, damage: float, blast_radius: float):
        self.position = position
        self.velocity = velocity
        self.weight = weight
        self.damage = damage
        self.blast_radius = blast_radius

    def update(self, dt: float) -> None:
        """Advance position by one simulation step. Implemented in Phase 3."""
        raise NotImplementedError("Projectile motion lands in Phase 3")

    def explode(self):
        """Resolve impact into an explosion point. Implemented in Phase 3."""
        raise NotImplementedError("Explosions land in Phase 3")
