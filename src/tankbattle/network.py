"""Length-prefixed JSON message framing shared by server.py and client.py.

TCP is a byte stream, not a message stream, so each message is sent as a 4-byte
big-endian length header followed by that many bytes of UTF-8 JSON.
"""

import json
import socket

_HEADER_SIZE = 4


def send_message(sock: socket.socket, message: dict) -> None:
    """Serialize and send a message over the socket."""
    payload = json.dumps(message).encode("utf-8")
    header = len(payload).to_bytes(_HEADER_SIZE, "big")
    sock.sendall(header + payload)


def receive_message(sock: socket.socket) -> dict | None:
    """Receive and deserialize one message, or None if the peer closed the connection."""
    header = _receive_exact(sock, _HEADER_SIZE)
    if header is None:
        return None
    length = int.from_bytes(header, "big")
    payload = _receive_exact(sock, length)
    if payload is None:
        return None
    return json.loads(payload.decode("utf-8"))


def _receive_exact(sock: socket.socket, size: int) -> bytes | None:
    chunks = bytearray()
    while len(chunks) < size:
        chunk = sock.recv(size - len(chunks))
        if not chunk:
            return None
        chunks.extend(chunk)
    return bytes(chunks)
