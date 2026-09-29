"""A player and the tank they control."""

from tankbattle.models.tank import Tank


class Player:
    """A participant: an id, a display name and the tank they control."""

    def __init__(self, player_id: int, name: str, tank: Tank):
        self.player_id = player_id
        self.name = name
        self.tank = tank
