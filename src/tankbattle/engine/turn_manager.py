"""Tracks whose turn it is and advances turns."""

from tankbattle.models.player import Player


class TurnManager:
    def __init__(self, players: list[Player]):
        if not players:
            raise ValueError("TurnManager needs at least one player")
        self.players = players
        self._current_index = 0

    @property
    def current_player(self) -> Player:
        return self.players[self._current_index]

    def end_turn(self) -> None:
        self._current_index = (self._current_index + 1) % len(self.players)
