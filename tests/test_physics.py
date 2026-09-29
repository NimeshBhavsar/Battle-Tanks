import pytest

from tankbattle.engine import physics
from tankbattle.models.ammunition import HeavyShell, LightShell, MediumShell
from tankbattle.models.projectile import Projectile
from tankbattle.utils.constants import AMMO_WEIGHT_GRAVITY_SCALE, TRAJECTORY_MAX_POINTS


class TestLaunchVelocity:
    def test_zero_degrees_points_right(self):
        vx, vy = physics.launch_velocity(10, 0)
        assert vx == pytest.approx(10)
        assert vy == pytest.approx(0)

    def test_ninety_degrees_points_up(self):
        vx, vy = physics.launch_velocity(10, 90)
        assert vx == pytest.approx(0)
        assert vy == pytest.approx(-10)  # screen y grows downward, so up is negative

    def test_one_eighty_points_left(self):
        vx, vy = physics.launch_velocity(10, 180)
        assert vx == pytest.approx(-10)
        assert vy == pytest.approx(0)

    def test_speed_is_preserved_at_any_angle(self):
        vx, vy = physics.launch_velocity(20, 37)
        assert (vx**2 + vy**2) ** 0.5 == pytest.approx(20)


class TestStep:
    def test_moves_by_velocity_then_applies_gravity(self):
        position, velocity = physics.step((0, 0), (3, -4), 0.1)
        assert position == (3, -4)
        assert velocity == pytest.approx((3, -4 + physics.GRAVITY_CONSTANT * 0.1))

    def test_horizontal_velocity_is_unchanged(self):
        _, velocity = physics.step((0, 0), (3, -4), 0.5)
        assert velocity[0] == 3

    def test_heavier_weight_accelerates_downward_faster(self):
        _, light = physics.step((0, 0), (0, 0), 1 * AMMO_WEIGHT_GRAVITY_SCALE)
        _, heavy = physics.step((0, 0), (0, 0), 6 * AMMO_WEIGHT_GRAVITY_SCALE)
        assert heavy[1] > light[1] > 0

    def test_zero_weight_factor_means_no_gravity(self):
        _, velocity = physics.step((0, 0), (1, -1), 0)
        assert velocity == (1, -1)


class TestProjectile:
    @pytest.mark.parametrize("shell, expected_radius", [(LightShell, 4), (MediumShell, 7), (HeavyShell, 10)])
    def test_radius_grows_with_weight(self, shell, expected_radius):
        ammo = shell()
        projectile = Projectile((0, 0), (0, 0), ammo.weight, ammo.damage, ammo.blast_radius)
        assert projectile.radius == expected_radius

    def test_update_advances_the_position(self):
        projectile = Projectile((10, 10), (2, -3), 1, 30, 20)
        projectile.update()
        assert projectile.position == (12, 7)

    def test_a_heavy_shell_falls_faster_than_a_light_one(self):
        light = Projectile((0, 0), (5, 0), 1, 30, 20)
        heavy = Projectile((0, 0), (5, 0), 6, 70, 40)
        for _ in range(20):
            light.update()
            heavy.update()
        assert heavy.position[1] > light.position[1]

    def test_explode_marks_it_spent_and_returns_the_position(self):
        projectile = Projectile((5, 6), (0, 0), 1, 30, 20)
        assert not projectile.exploded
        assert projectile.explode() == (5, 6)
        assert projectile.exploded


class TestTrajectoryPreview:
    def test_preview_has_points_but_not_too_many(self, tank, flat_terrain):
        points = tank.preview_trajectory(flat_terrain)
        assert 0 < len(points) <= TRAJECTORY_MAX_POINTS

    def test_preview_starts_near_the_barrel_tip(self, tank, flat_terrain):
        tip_x, tip_y = tank.barrel_tip()
        first_x, first_y = tank.preview_trajectory(flat_terrain)[0]
        assert abs(first_x - tip_x) < 30 and abs(first_y - tip_y) < 30

    def test_preview_matches_the_real_shell_path(self, tank, flat_terrain):
        """The aiming arc must use the same physics as the fired shell."""
        from tankbattle.utils.constants import TRAJECTORY_STEPS_PER_POINT

        tank.angle, tank.power = 60, 70
        preview = tank.preview_trajectory(flat_terrain)
        shell = tank.fire()
        shell.update()  # the first preview point is recorded after one step...
        assert shell.position == pytest.approx(preview[0])
        for expected in preview[1:5]:
            for _ in range(TRAJECTORY_STEPS_PER_POINT):  # ...and then one point every few steps
                shell.update()
            assert shell.position == pytest.approx(expected)
