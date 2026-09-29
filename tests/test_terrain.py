import pytest

from tankbattle.engine import terrain_engine
from tankbattle.models.terrain import Terrain
from tankbattle.utils.constants import SCREEN_HEIGHT, SCREEN_WIDTH


class TestGeneration:
    def test_one_height_per_column(self):
        terrain = Terrain(seed=1)
        assert len(terrain.height_map) == SCREEN_WIDTH == terrain.width

    def test_same_seed_gives_the_same_terrain(self):
        assert Terrain(seed=3).height_map == Terrain(seed=3).height_map

    def test_different_seeds_give_different_terrain(self):
        assert Terrain(seed=3).height_map != Terrain(seed=4).height_map

    def test_heights_stay_on_screen(self):
        terrain = Terrain(seed=5)
        assert all(0 < h < SCREEN_HEIGHT for h in terrain.height_map)

    def test_terrain_is_smooth(self):
        terrain = Terrain(seed=6)
        steps = [abs(a - b) for a, b in zip(terrain.height_map, terrain.height_map[1:])]
        assert max(steps) <= 8  # no cliffs: the generator smooths the random walk


class TestHeightAt:
    def test_reads_the_column(self, flat_terrain):
        flat_terrain.height_map[10] = 123
        assert flat_terrain.height_at(10) == 123

    def test_out_of_range_is_clamped_to_the_edges(self, flat_terrain):
        flat_terrain.height_map[0] = 111
        flat_terrain.height_map[-1] = 222
        assert flat_terrain.height_at(-50) == 111
        assert flat_terrain.height_at(flat_terrain.width + 50) == 222

    def test_collision_is_at_or_below_the_ground(self, flat_terrain):
        assert flat_terrain.collision(100, 400)
        assert flat_terrain.collision(100, 500)
        assert not flat_terrain.collision(100, 399)


class TestCraters:
    def test_center_column_drops_by_the_radius(self, flat_terrain):
        terrain_engine.carve_crater(flat_terrain, 500, 400, 30)
        assert flat_terrain.height_at(500) == 430

    def test_crater_is_round(self, flat_terrain):
        terrain_engine.carve_crater(flat_terrain, 500, 400, 30)
        depth_at = lambda dx: flat_terrain.height_at(500 + dx) - 400  # noqa: E731
        assert depth_at(0) > depth_at(15) > depth_at(29) >= 0

    def test_ground_outside_the_radius_is_untouched(self, flat_terrain):
        terrain_engine.carve_crater(flat_terrain, 500, 400, 30)
        assert flat_terrain.height_at(469) == 400
        assert flat_terrain.height_at(531) == 400

    def test_a_crater_never_raises_the_ground(self, flat_terrain):
        terrain_engine.carve_crater(flat_terrain, 500, 300, 30)  # explosion high above the ground
        assert all(h >= 400 for h in flat_terrain.height_map)

    def test_ground_is_never_dug_below_the_screen(self, flat_terrain):
        terrain_engine.carve_crater(flat_terrain, 500, flat_terrain.height, 80)
        assert max(flat_terrain.height_map) <= flat_terrain.height

    @pytest.mark.parametrize("x", [0, 5, -10, SCREEN_WIDTH - 1, SCREEN_WIDTH + 10])
    def test_craters_at_the_edges_do_not_crash(self, flat_terrain, x):
        terrain_engine.carve_crater(flat_terrain, x, 400, 40)
        assert len(flat_terrain.height_map) == SCREEN_WIDTH

    def test_overlapping_craters_keep_the_deeper_one(self, flat_terrain):
        terrain_engine.carve_crater(flat_terrain, 500, 400, 50)
        deep = flat_terrain.height_at(500)
        terrain_engine.carve_crater(flat_terrain, 500, 400, 10)
        assert flat_terrain.height_at(500) == deep
