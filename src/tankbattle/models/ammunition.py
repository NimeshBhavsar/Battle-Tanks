"""Ammo types. Weight affects projectile motion (see engine.physics), used starting in Phase 3."""


class Ammo:
    def __init__(self, name: str, weight: float, damage: float, blast_radius: float, sprite=None):
        self.name = name
        self.weight = weight
        self.damage = damage
        self.blast_radius = blast_radius
        self.sprite = sprite


class LightShell(Ammo):
    def __init__(self):
        super().__init__(name="Light", weight=1, damage=20, blast_radius=20)


class MediumShell(Ammo):
    def __init__(self):
        super().__init__(name="Medium", weight=3, damage=40, blast_radius=35)


class HeavyShell(Ammo):
    def __init__(self):
        super().__init__(name="Heavy", weight=6, damage=70, blast_radius=50)


AMMO_BY_NAME: dict[str, type[Ammo]] = {"Light": LightShell, "Medium": MediumShell, "Heavy": HeavyShell}
