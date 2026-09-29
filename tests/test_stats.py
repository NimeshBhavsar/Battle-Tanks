import json

import pytest

from tankbattle.server import build_players
from tankbattle.stats import MatchRecorder, load_match, save_match, summarize


@pytest.fixture
def players(flat_terrain):
    players = build_players(flat_terrain)
    players[0].name, players[1].name = "Alice", "Bob"
    return players


def record(recorder, shooter, damage_to_1, damage_to_2, ammo="Light", angle=45.0, power=50.0):
    recorder.start_shot(shooter, ammo, angle, power)
    recorder.finish_shot({1: damage_to_1, 2: damage_to_2})


class TestRecordingShots:
    def test_a_hit_is_damage_to_the_opponent(self):
        recorder = MatchRecorder()
        record(recorder, shooter=1, damage_to_1=0, damage_to_2=30)
        shot = recorder.shots[0]
        assert shot["hit"] is True
        assert shot["damage_dealt"] == 30

    def test_a_miss_records_zero(self):
        recorder = MatchRecorder()
        record(recorder, shooter=1, damage_to_1=0, damage_to_2=0)
        assert recorder.shots[0]["hit"] is False and recorder.shots[0]["damage_dealt"] == 0

    def test_hurting_yourself_is_not_a_hit(self):
        recorder = MatchRecorder()
        record(recorder, shooter=1, damage_to_1=20, damage_to_2=0)
        shot = recorder.shots[0]
        assert shot["hit"] is False
        assert shot["damage"]["1"] == 20  # the self-damage is still logged

    def test_shot_details_are_stored(self):
        recorder = MatchRecorder()
        record(recorder, shooter=2, damage_to_1=10, damage_to_2=0, ammo="Heavy", angle=123.456, power=77.77)
        shot = recorder.shots[0]
        assert (shot["player_id"], shot["ammo"], shot["angle"], shot["power"]) == (2, "Heavy", 123.5, 77.8)

    def test_shots_are_numbered_in_order(self):
        recorder = MatchRecorder()
        for _ in range(3):
            record(recorder, 1, 0, 0)
        assert [s["n"] for s in recorder.shots] == [1, 2, 3]

    def test_times_never_go_backwards(self):
        recorder = MatchRecorder()
        for _ in range(3):
            record(recorder, 1, 0, 0)
        times = [s["time_s"] for s in recorder.shots]
        assert times == sorted(times)

    def test_finishing_without_a_started_shot_does_nothing(self):
        recorder = MatchRecorder()
        recorder.finish_shot({1: 0, 2: 10})
        assert recorder.shots == []

    def test_a_shot_can_only_be_finished_once(self):
        recorder = MatchRecorder()
        recorder.start_shot(1, "Light", 45, 50)
        recorder.finish_shot({1: 0, 2: 10})
        recorder.finish_shot({1: 0, 2: 10})
        assert len(recorder.shots) == 1


class TestFinish:
    def test_summary_of_the_whole_match(self, players):
        recorder = MatchRecorder()
        record(recorder, 1, 0, 30)
        players[1].tank.health = 70
        match = recorder.finish(players, winner_id=1)
        assert match["winner_id"] == 1
        assert match["players"]["1"]["name"] == "Alice"
        assert match["players"]["2"]["final_health"] == 70
        assert len(match["shots"]) == 1
        assert match["duration_s"] >= 0

    def test_a_draw_has_no_winner(self, players):
        assert MatchRecorder().finish(players, winner_id=None)["winner_id"] is None

    def test_the_match_is_json_serializable(self, players):
        recorder = MatchRecorder()
        record(recorder, 1, 0, 30)
        json.dumps(recorder.finish(players, 1))


class TestSaveAndLoad:
    def test_round_trip(self, players, tmp_path):
        recorder = MatchRecorder()
        record(recorder, 1, 0, 30)
        match = recorder.finish(players, 1)
        path = save_match(match, tmp_path)
        assert load_match(path) == match

    def test_file_is_named_after_the_start_time(self, players, tmp_path):
        path = save_match(MatchRecorder().finish(players, None), tmp_path)
        assert path.parent == tmp_path
        assert path.name.startswith("match_") and path.suffix == ".json"

    def test_missing_folder_is_created(self, players, tmp_path):
        target = tmp_path / "nested" / "stats"
        save_match(MatchRecorder().finish(players, None), target)
        assert target.is_dir()


class TestSummarize:
    def test_accuracy_and_damage_per_player(self, players):
        recorder = MatchRecorder()
        record(recorder, 1, 0, 30)  # Alice hits
        record(recorder, 2, 0, 0)  # Bob misses
        record(recorder, 1, 0, 0)  # Alice misses
        record(recorder, 1, 0, 20)  # Alice hits
        summary = summarize(recorder.finish(players, 1))
        assert summary[1] == {
            "name": "Alice",
            "shots": 3,
            "hits": 2,
            "accuracy": pytest.approx(2 / 3),
            "damage_dealt": 50,
        }
        assert summary[2]["shots"] == 1 and summary[2]["accuracy"] == 0

    def test_a_player_who_never_fired_has_zero_accuracy(self, players):
        summary = summarize(MatchRecorder().finish(players, None))
        assert summary[1]["accuracy"] == 0 and summary[1]["shots"] == 0
