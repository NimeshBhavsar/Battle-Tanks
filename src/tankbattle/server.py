"""Authoritative game server: owns physics, collision, and turn state. Implemented in Phase 6."""


class GameServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def start(self) -> None:
        """Accept client connections and run the authoritative game loop. Implemented in Phase 6."""
        raise NotImplementedError("The server lands in Phase 6")
