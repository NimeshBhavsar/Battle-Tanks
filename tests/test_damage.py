import pytest

from tankbattle.engine.damage import calculate_damage, distance_to_tank
from tankbattle.models.ammunition import AMMO_BY_NAME, Ammo, HeavyShell, LightShell, MediumShell


class TestCalculateDamage:
    def test_full_damage_at_the_center(self):
        assert calculate_damage(0, 20, 30) == 30

    def test_half_damage_halfway_out(self):
        assert calculate_damage(10, 20, 30) == pytest.approx(15)

    def test_no_damage_at_the_edge(self):
        assert calculate_damage(20, 20, 30) == 0

    def test_no_damage_beyond_the_blast(self):
        assert calculate_damage(50, 20, 30) == 0

    def test_zero_radius_never_damages(self):
        assert calculate_damage(0, 0, 30) == 0

    def test_damage_never_increases_with_distance(self):
        values = [calculate_damage(d, 40, 70) for d in range(0, 60, 5)]
        assert values == sorted(values, reverse=True)


class TestDistanceToTank:
    """The tank in the fixture is at (500, 400): body x 480-520, y 380-400, barrel at 45 degrees."""

    def test_inside_the_body_is_zero(self, tank):
        assert distance_to_tank((500, 390), tank) == 0

    def test_beside_the_body_is_the_gap(self, tank):
        assert distance_to_tank((530, 390), tank) == pytest.approx(10)

    def test_below_the_body_is_the_gap(self, tank):
        assert distance_to_tank((500, 415), tank) == pytest.approx(15)

    def test_the_barrel_counts_as_part_of_the_tank(self, tank):
        assert distance_to_tank(tank.barrel_tip(), tank) == pytest.approx(0, abs=1e-9)

    def test_the_barrel_can_be_the_nearest_part(self, tank):
        # a point just past the barrel tip is much closer to the barrel than to the body rectangle
        tip_x, tip_y = tank.barrel_tip()
        point = (tip_x + 3, tip_y - 3)
        assert distance_to_tank(point, tank) < 5

    def test_far_away_is_far(self, tank):
        assert distance_to_tank((900, 400), tank) > 300


class TestAmmunition:
    def test_lookup_table_names(self):
        assert set(AMMO_BY_NAME) == {"Light", "Medium", "Heavy"}

    @pytest.mark.parametrize("shell", [LightShell, MediumShell, HeavyShell])
    def test_every_shell_is_an_ammo(self, shell):
        assert isinstance(shell(), Ammo)

    @pytest.mark.parametrize("name", ["Light", "Medium", "Heavy"])
    def test_lookup_builds_the_matching_shell(self, name):
        assert AMMO_BY_NAME[name]().name == name

    def test_heavier_shells_hit_harder_and_blast_wider(self):
        light, medium, heavy = LightShell(), MediumShell(), HeavyShell()
        assert light.weight < medium.weight < heavy.weight
        assert light.damage < medium.damage < heavy.damage
        assert light.blast_radius < medium.blast_radius <= heavy.blast_radius

    def test_each_call_creates_an_independent_shell(self):
        first, second = LightShell(), LightShell()
        first.damage = 999
        assert second.damage != 999
