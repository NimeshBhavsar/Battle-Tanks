"""Distance-based damage falloff from an explosion: full damage at the center, none past blast_radius."""


def calculate_damage(distance: float, blast_radius: float, max_damage: float) -> float:
    """Damage dealt to a tank at `distance` from the blast center."""
    if blast_radius <= 0 or distance >= blast_radius:
        return 0.0
    falloff = 1 - (distance / blast_radius)
    return max_damage * falloff
