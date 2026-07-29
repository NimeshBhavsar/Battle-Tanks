"""Networked client: renders the state it receives and sends player input. Implemented in Phase 6."""


class GameClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def connect(self) -> None:
        """Connect to the game server and start the render/input loop. Implemented in Phase 6."""
        raise NotImplementedError("The networked client lands in Phase 6")
