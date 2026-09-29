import math

import pytest

from tankbattle.utils.helpers import clamp, distance, distance_to_segment


class TestClamp:
    def test_inside_range_is_unchanged(self):
        assert clamp(5, 0, 10) == 5

    def test_below_minimum(self):
        assert clamp(-3, 0, 10) == 0

    def test_above_maximum(self):
        assert clamp(99, 0, 10) == 10

    def test_bounds_are_inclusive(self):
        assert clamp(0, 0, 10) == 0
        assert clamp(10, 0, 10) == 10


class TestDistance:
    def test_three_four_five(self):
        assert distance((0, 0), (3, 4)) == 5

    def test_same_point_is_zero(self):
        assert distance((7, 7), (7, 7)) == 0

    def test_is_symmetric(self):
        assert distance((1, 2), (5, 9)) == distance((5, 9), (1, 2))


class TestDistanceToSegment:
    def test_perpendicular_to_the_middle(self):
        assert distance_to_segment((5, 3), (0, 0), (10, 0)) == 3

    def test_beyond_the_end_measures_to_the_endpoint(self):
        assert distance_to_segment((13, 4), (0, 0), (10, 0)) == 5

    def test_before_the_start_measures_to_the_start(self):
        assert distance_to_segment((-3, -4), (0, 0), (10, 0)) == 5

    def test_point_on_the_segment_is_zero(self):
        assert distance_to_segment((4, 0), (0, 0), (10, 0)) == 0

    def test_zero_length_segment_is_point_distance(self):
        assert distance_to_segment((3, 4), (0, 0), (0, 0)) == 5

    def test_diagonal_segment(self):
        # distance from (0, 2) to the line y = x is 2 / sqrt(2)
        assert distance_to_segment((0, 2), (0, 0), (10, 10)) == pytest.approx(math.sqrt(2))
