"""Ammo types. Weight affects projectile motion (see engine.physics), used starting in Phase 3."""


class Ammo:
    """Base shell type: the stats a projectile reads when it is fired."""

    def __init__(self, name: str, weight: float, damage: float, blast_radius: float, sprite=None):
        self.name = name
        self.weight = weight
        self.damage = damage
        self.blast_radius = blast_radius
        self.sprite = sprite


class LightShell(Ammo):
    """Light shell: fast and small, with the least damage."""

    def __init__(self):
        super().__init__(name="Light", weight=1, damage=30, blast_radius=20)


class MediumShell(Ammo):
    """Medium shell: a balance of damage and blast size."""

    def __init__(self):
        super().__init__(name="Medium", weight=3, damage=40, blast_radius=35)


class HeavyShell(Ammo):
    """Heavy shell: slow and large, with the most damage."""

    def __init__(self):
        super().__init__(name="Heavy", weight=6, damage=70, blast_radius=40)


AMMO_BY_NAME: dict[str, type[Ammo]] = {"Light": LightShell, "Medium": MediumShell, "Heavy": HeavyShell}
