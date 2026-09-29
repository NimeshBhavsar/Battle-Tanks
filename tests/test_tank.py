import pytest

from tankbattle.models.ammunition import HeavyShell
from tankbattle.settings import TANK_START_FUEL, TANK_START_HEALTH
from tankbattle.utils.constants import (
    BARREL_LENGTH,
    LAUNCH_POWER_SCALE,
    TANK_FUEL_COST_PER_FRAME,
    TANK_MAX_ANGLE,
    TANK_MOVE_SPEED,
    TANK_POWER_MAX,
    TANK_WIDTH,
)


class TestMovement:
    def test_moving_shifts_the_tank_and_burns_fuel(self, tank, flat_terrain):
        tank.move(1, flat_terrain)
        assert tank.position[0] == 500 + TANK_MOVE_SPEED
        assert tank.fuel == TANK_START_FUEL - TANK_FUEL_COST_PER_FRAME

    def test_moving_left_goes_the_other_way(self, tank, flat_terrain):
        tank.move(-1, flat_terrain)
        assert tank.position[0] == 500 - TANK_MOVE_SPEED

    def test_no_fuel_means_no_movement(self, tank, flat_terrain):
        tank.fuel = 0
        tank.move(1, flat_terrain)
        assert tank.position[0] == 500

    def test_direction_zero_does_nothing(self, tank, flat_terrain):
        tank.move(0, flat_terrain)
        assert tank.position == (500, 400) and tank.fuel == TANK_START_FUEL

    def test_tank_stays_inside_the_map(self, tank, flat_terrain):
        tank.position = (TANK_WIDTH / 2, 400)
        tank.move(-1, flat_terrain)
        assert tank.position[0] == TANK_WIDTH / 2
        tank.position = (flat_terrain.width - TANK_WIDTH / 2, 400)
        tank.move(1, flat_terrain)
        assert tank.position[0] == flat_terrain.width - TANK_WIDTH / 2

    def test_tank_follows_the_ground_height(self, tank, flat_terrain):
        flat_terrain.height_map[503] = 350
        tank.move(1, flat_terrain)
        assert tank.position == (503, 350)

    def test_fuel_never_goes_negative(self, tank, flat_terrain):
        tank.fuel = 0.2
        tank.move(1, flat_terrain)
        assert tank.fuel == 0


class TestAiming:
    def test_barrel_rotates_and_clamps(self, tank):
        tank.angle = 0
        tank.rotate_barrel(-1)
        assert tank.angle == 0
        tank.angle = TANK_MAX_ANGLE
        tank.rotate_barrel(1)
        assert tank.angle == TANK_MAX_ANGLE
        tank.angle = 90
        tank.rotate_barrel(1)
        assert tank.angle > 90

    def test_power_adjusts_and_clamps(self, tank):
        tank.power = TANK_POWER_MAX
        tank.adjust_power(1)
        assert tank.power == TANK_POWER_MAX
        tank.power = 0
        tank.adjust_power(-1)
        assert tank.power == 0
        tank.power = 50
        tank.adjust_power(1)
        assert tank.power > 50

    def test_barrel_tip_points_right_at_zero_degrees(self, tank):
        tank.angle = 0
        rect = tank.get_rect()
        assert tank.barrel_tip() == pytest.approx((rect.centerx + BARREL_LENGTH, rect.centery))

    def test_barrel_tip_is_above_the_tank_at_ninety_degrees(self, tank):
        tank.angle = 90
        rect = tank.get_rect()
        assert tank.barrel_tip() == pytest.approx((rect.centerx, rect.centery - BARREL_LENGTH))

    def test_rect_sits_on_the_tank_position(self, tank):
        assert tank.get_rect().midbottom == (500, 400)


class TestFiring:
    def test_shell_starts_at_the_barrel_tip(self, tank):
        assert tank.fire().position == tank.barrel_tip()

    def test_straight_up_has_only_vertical_speed(self, tank):
        tank.angle, tank.power = 90, 100
        vx, vy = tank.fire().velocity
        assert vx == pytest.approx(0, abs=1e-9)
        assert vy == pytest.approx(-100 * LAUNCH_POWER_SCALE)

    def test_more_power_means_a_faster_shell(self, tank):
        tank.power = 40
        slow = tank.fire().velocity
        tank.power = 80
        fast = tank.fire().velocity
        assert abs(fast[0]) > abs(slow[0])

    def test_shell_takes_the_selected_ammos_stats(self, tank):
        tank.current_ammo = HeavyShell()
        shell = tank.fire()
        assert (shell.weight, shell.damage, shell.blast_radius) == (6, 70, 40)


class TestHealth:
    def test_new_tank_is_alive_and_full(self, tank):
        assert tank.alive and tank.health == TANK_START_HEALTH

    def test_damage_reduces_health(self, tank):
        tank.take_damage(30)
        assert tank.health == TANK_START_HEALTH - 30 and tank.alive

    def test_health_stops_at_zero_and_the_tank_dies(self, tank):
        tank.take_damage(9999)
        assert tank.health == 0 and not tank.alive
