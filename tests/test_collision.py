import pytest

from tankbattle.engine.collision import check_collision
from tankbattle.models.projectile import Projectile
from tankbattle.utils.constants import TANK_HITBOX_PADDING


def shell_at(x, y, weight=1):
    return Projectile((x, y), (0, 0), weight, 30, 20)


class TestTankHits:
    """The tank in the fixture is at (500, 400): body x 480-520, y 380-400."""

    def test_shell_inside_the_body_hits(self, tank, flat_terrain):
        assert check_collision(shell_at(500, 390), flat_terrain, [tank]) == (500, 390)

    def test_padding_makes_a_near_miss_count(self, tank, flat_terrain):
        # 4 px shell radius + padding reaches above the top edge (y=380)
        reach = tank.get_rect().top - TANK_HITBOX_PADDING - 4
        assert check_collision(shell_at(500, reach + 1), flat_terrain, [tank]) is not None

    def test_just_outside_the_padding_misses(self, tank, flat_terrain):
        reach = tank.get_rect().top - TANK_HITBOX_PADDING - 4
        tank.angle = 0  # keep the barrel out of the way
        assert check_collision(shell_at(500, reach - 20), flat_terrain, [tank]) is None

    def test_a_bigger_shell_reaches_further(self, tank, flat_terrain):
        tank.angle = 0
        y = tank.get_rect().top - 20
        assert check_collision(shell_at(500, y, weight=1), flat_terrain, [tank]) is None
        assert check_collision(shell_at(500, y, weight=6), flat_terrain, [tank]) is not None

    def test_the_barrel_can_be_hit(self, tank, flat_terrain):
        tank.angle = 90  # barrel straight up from the body center
        assert check_collision(shell_at(500, 350), flat_terrain, [tank]) is not None

    def test_far_above_the_barrel_misses(self, tank, flat_terrain):
        tank.angle = 90
        assert check_collision(shell_at(500, 320), flat_terrain, [tank]) is None

    def test_no_tanks_to_hit(self, flat_terrain):
        assert check_collision(shell_at(500, 300), flat_terrain, []) is None


class TestWorldHits:
    def test_shell_in_the_air_does_not_collide(self, flat_terrain):
        assert check_collision(shell_at(100, 200), flat_terrain, []) is None

    def test_shell_reaching_the_ground_explodes(self, flat_terrain):
        assert check_collision(shell_at(100, 400), flat_terrain, []) == (100, 400)

    def test_shell_below_the_ground_explodes(self, flat_terrain):
        assert check_collision(shell_at(100, 450), flat_terrain, []) is not None

    @pytest.mark.parametrize("x", [-5, 1030])
    def test_leaving_the_map_sideways_explodes(self, flat_terrain, x):
        assert check_collision(shell_at(x, 100), flat_terrain, []) is not None

    def test_a_crater_lets_a_shell_fall_deeper(self, flat_terrain):
        shell = shell_at(500, 420)
        assert check_collision(shell, flat_terrain, []) is not None  # inside the ground: hit
        flat_terrain.height_map[500] = 440  # a crater deepens the ground here
        assert check_collision(shell, flat_terrain, []) is None  # now it is still in the air
