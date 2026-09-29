import pytest

from tankbattle.report import build_report, save_report
from tankbattle.server import build_players
from tankbattle.stats import MatchRecorder

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def make_match(flat_terrain, shots, winner_id=1, names=("Alice", "Bob")):
    players = build_players(flat_terrain)
    players[0].name, players[1].name = names
    recorder = MatchRecorder()
    for shooter, to_1, to_2 in shots:
        recorder.start_shot(shooter, "Medium", 60.0, 70.0)
        recorder.finish_shot({1: to_1, 2: to_2})
    return recorder.finish(players, winner_id)


def test_report_is_a_png(flat_terrain):
    match = make_match(flat_terrain, [(1, 0, 30), (2, 0, 0), (1, 0, 40)])
    assert build_report(match).startswith(PNG_SIGNATURE)


def test_a_match_with_no_shots_still_draws(flat_terrain):
    assert build_report(make_match(flat_terrain, [], winner_id=None)).startswith(PNG_SIGNATURE)


def test_a_draw_still_draws(flat_terrain):
    assert build_report(make_match(flat_terrain, [(1, 20, 20)], winner_id=None)).startswith(PNG_SIGNATURE)


def test_a_dollar_sign_in_a_name_does_not_break_matplotlib(flat_terrain):
    match = make_match(flat_terrain, [(1, 0, 30)], names=("$ilver", "B$b"))
    assert build_report(match).startswith(PNG_SIGNATURE)


def test_a_player_who_never_hit_anything(flat_terrain):
    match = make_match(flat_terrain, [(1, 0, 0), (2, 0, 0)], winner_id=None)
    assert build_report(match).startswith(PNG_SIGNATURE)


def test_save_report_writes_the_file(flat_terrain, tmp_path):
    match = make_match(flat_terrain, [(1, 0, 30)])
    path = save_report(match, tmp_path / "chart.png")
    assert path.read_bytes().startswith(PNG_SIGNATURE)


def test_the_committed_sample_match_can_be_charted():
    """docs/sample_match.json is what the README shows; it must stay loadable by the current code."""
    from pathlib import Path

    from tankbattle.stats import load_match

    sample = Path(__file__).resolve().parent.parent / "docs" / "sample_match.json"
    if not sample.exists():
        pytest.skip("sample match not present")
    assert build_report(load_match(sample)).startswith(PNG_SIGNATURE)
