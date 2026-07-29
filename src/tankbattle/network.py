"""Socket message framing/serialization shared by server.py and client.py. Implemented in Phase 6."""


def send_message(sock, message: dict) -> None:
    """Serialize and send a message over the socket. Implemented in Phase 6."""
    raise NotImplementedError("Networking lands in Phase 6")


def receive_message(sock) -> dict:
    """Receive and deserialize a message from the socket. Implemented in Phase 6."""
    raise NotImplementedError("Networking lands in Phase 6")
