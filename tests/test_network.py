import socket

import pytest

from tankbattle import network


@pytest.fixture
def pair():
    a, b = socket.socketpair()
    a.settimeout(2)
    b.settimeout(2)
    yield a, b
    a.close()
    b.close()


def test_a_message_round_trips(pair):
    sender, receiver = pair
    message = {"type": "state", "tanks": [{"player_id": 1, "position": [10.5, 20]}], "ok": True, "none": None}
    network.send_message(sender, message)
    assert network.receive_message(receiver) == message


def test_messages_keep_their_boundaries(pair):
    sender, receiver = pair
    for i in range(5):
        network.send_message(sender, {"n": i})
    assert [network.receive_message(receiver)["n"] for _ in range(5)] == [0, 1, 2, 3, 4]


def test_non_ascii_text_survives(pair):
    sender, receiver = pair
    network.send_message(sender, {"name": "Zoë — 坦克"})
    assert network.receive_message(receiver)["name"] == "Zoë — 坦克"


def test_a_large_message_is_reassembled(pair):
    sender, receiver = pair
    big = {"terrain": list(range(200_000))}  # far larger than one socket read
    import threading

    thread = threading.Thread(target=network.send_message, args=(sender, big))
    thread.start()
    assert network.receive_message(receiver) == big
    thread.join()


def test_a_closed_connection_returns_none(pair):
    sender, receiver = pair
    sender.close()
    assert network.receive_message(receiver) is None


def test_a_connection_closed_mid_message_returns_none(pair):
    sender, receiver = pair
    sender.sendall((100).to_bytes(4, "big") + b"only a few bytes")  # promises 100 bytes, sends 16
    sender.close()
    assert network.receive_message(receiver) is None
