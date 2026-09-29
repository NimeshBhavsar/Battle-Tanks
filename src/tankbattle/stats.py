"""Match statistics: a log of every shot fired, saved as JSON when the match ends.

The server owns the truth about what was fired and what it hit, so it feeds a
`MatchRecorder` during play. `report.py` turns the finished record into a chart.
"""

import datetime
import json
import time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tankbattle.models.player import Player

SCHEMA_VERSION = 1


class MatchRecorder:
    """Collects one record per shot: who fired what, how it was aimed and how much damage it did."""

    def __init__(self):
        self._started_monotonic = time.monotonic()
        self.started_at = datetime.datetime.now()
        self.shots: list[dict] = []
        self._open_shot: dict | None = None

    def start_shot(self, player_id: int, ammo: str, angle: float, power: float) -> None:
        """Note that a shell has just been fired; the outcome is filled in by `finish_shot`."""
        self._open_shot = {
            "player_id": player_id,
            "ammo": ammo,
            "angle": round(angle, 1),
            "power": round(power, 1),
            "time_s": round(time.monotonic() - self._started_monotonic, 2),
        }

    def finish_shot(self, damage_by_player: dict[int, float]) -> None:
        """Record the damage each player took from the shell that was just fired (0 for a miss)."""
        if self._open_shot is None:
            return
        shot, self._open_shot = self._open_shot, None
        dealt = sum(amount for player_id, amount in damage_by_player.items() if player_id != shot["player_id"])
        shot["n"] = len(self.shots) + 1
        shot["damage"] = {str(player_id): round(amount, 1) for player_id, amount in damage_by_player.items()}
        shot["damage_dealt"] = round(dealt, 1)
        shot["hit"] = dealt > 0
        self.shots.append(shot)

    def finish(self, players: list["Player"], winner_id: int | None) -> dict:
        """Package everything into a JSON-serializable dict describing the whole match."""
        return {
            "version": SCHEMA_VERSION,
            "started_at": self.started_at.isoformat(timespec="seconds"),
            "duration_s": round(time.monotonic() - self._started_monotonic, 1),
            "winner_id": winner_id,
            "players": {
                str(player.player_id): {
                    "name": player.name,
                    "color": list(player.tank.color),
                    "final_health": round(player.tank.health, 1),
                }
                for player in players
            },
            "shots": self.shots,
        }


def save_match(match: dict, directory: str | Path) -> Path:
    """Write the match to `<directory>/match_<start time>.json` and return that path."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    stamp = match["started_at"].replace(":", "").replace("-", "").replace("T", "_")
    path = directory / f"match_{stamp}.json"
    path.write_text(json.dumps(match, indent=2), encoding="utf-8")
    return path


def load_match(path: str | Path) -> dict:
    """Read a match saved by `save_match`."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def summarize(match: dict) -> dict[int, dict]:
    """Per-player totals: shots, hits, accuracy (0-1) and total damage dealt."""
    summary = {}
    for key, info in match["players"].items():
        player_id = int(key)
        shots = [s for s in match["shots"] if s["player_id"] == player_id]
        hits = [s for s in shots if s["hit"]]
        summary[player_id] = {
            "name": info["name"],
            "shots": len(shots),
            "hits": len(hits),
            "accuracy": len(hits) / len(shots) if shots else 0.0,
            "damage_dealt": sum(s["damage_dealt"] for s in shots),
        }
    return summary
