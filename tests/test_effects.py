import pygame
import pytest

from tankbattle.ui.effects import Effects
from tankbattle.utils.constants import HIT_FLASH_FRAMES, MAX_PARTICLES, SHAKE_FRAMES


def run(effects, frames):
    for _ in range(frames):
        effects.update()


class TestParticles:
    def test_a_smoke_trail_adds_a_particle_that_fades_away(self):
        effects = Effects()
        effects.add_smoke_trail((100, 100), weight=3)
        assert len(effects.particles) == 1
        run(effects, 100)
        assert effects.particles == []

    def test_an_explosion_throws_up_debris_and_smoke(self):
        effects = Effects()
        effects.add_explosion((100, 100), blast_radius=40)
        assert len(effects.particles) > 20

    def test_bigger_blasts_throw_more_particles(self):
        small, big = Effects(), Effects()
        small.add_explosion((100, 100), 20)
        big.add_explosion((100, 100), 40)
        assert len(big.particles) > len(small.particles)

    def test_debris_flies_upward_at_first_then_falls(self):
        effects = Effects()
        effects.add_explosion((100, 100), 40)
        debris = [p for p in effects.particles if p.gravity > 0]
        assert debris and all(p.vy < 0 for p in debris)
        start_y = {id(p): p.y for p in debris}
        run(effects, 30)
        assert any(p.y > start_y[id(p)] - 1 for p in effects.particles if id(p) in start_y)

    def test_the_particle_count_is_capped(self):
        effects = Effects()
        for _ in range(MAX_PARTICLES * 3):
            effects.add_smoke_trail((0, 0), 1)
        assert len(effects.particles) == MAX_PARTICLES

    def test_all_particles_eventually_expire(self):
        effects = Effects()
        effects.add_explosion((100, 100), 40)
        run(effects, 200)
        assert effects.particles == []

    def test_drawing_does_not_raise(self):
        effects = Effects()
        effects.add_explosion((50, 50), 40)
        effects.add_smoke_trail((60, 60), 6)
        surface = pygame.Surface((200, 200))
        for _ in range(10):
            effects.update()
            effects.draw_particles(surface)

    def test_particles_can_be_drawn_off_screen(self):
        effects = Effects()
        effects.add_explosion((-50, -50), 40)
        effects.draw_particles(pygame.Surface((100, 100)))


class TestScreenShake:
    def test_no_shake_by_default(self):
        assert Effects().shake_offset() == (0, 0)

    def test_an_explosion_shakes_the_screen(self):
        effects = Effects()
        effects.add_explosion((100, 100), 40)
        assert any(effects.shake_offset() != (0, 0) for _ in range(50))

    def test_the_shake_stays_within_its_strength(self):
        effects = Effects()
        effects.add_explosion((100, 100), 40)
        strength = 40 * 0.15
        for _ in range(100):
            dx, dy = effects.shake_offset()
            assert abs(dx) <= round(strength) and abs(dy) <= round(strength)

    def test_the_shake_stops(self):
        effects = Effects()
        effects.add_explosion((100, 100), 40)
        run(effects, SHAKE_FRAMES + 2)
        assert effects.shake_offset() == (0, 0)

    def test_bigger_explosions_shake_harder(self):
        def peak(radius):
            effects = Effects()
            effects.add_explosion((100, 100), radius)
            return max(max(abs(v) for v in effects.shake_offset()) for _ in range(200))

        assert peak(80) > peak(10)


class TestHitFlash:
    def test_not_flashing_by_default(self):
        assert Effects().flash_progress(1) is None

    def test_flash_starts_at_zero_and_progresses(self):
        effects = Effects()
        effects.add_hit_flash(1)
        assert effects.flash_progress(1) == 0
        effects.update()
        assert 0 < effects.flash_progress(1) < 1

    def test_flash_ends(self):
        effects = Effects()
        effects.add_hit_flash(1)
        run(effects, HIT_FLASH_FRAMES)
        assert effects.flash_progress(1) is None

    def test_only_the_hit_tank_flashes(self):
        effects = Effects()
        effects.add_hit_flash(2)
        assert effects.flash_progress(1) is None and effects.flash_progress(2) == 0

    def test_a_second_hit_restarts_the_flash(self):
        effects = Effects()
        effects.add_hit_flash(1)
        run(effects, 5)
        effects.add_hit_flash(1)
        assert effects.flash_progress(1) == 0


@pytest.mark.parametrize("player_id", [1, 2])
def test_flash_drawing_does_not_raise(player_id, tank):
    from tankbattle.ui.game_screen import _draw_hit_flash

    _draw_hit_flash(pygame.Surface((1024, 576)), tank, 0.3)
