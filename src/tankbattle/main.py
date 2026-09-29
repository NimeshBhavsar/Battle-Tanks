"""CLI entry point: launches either the authoritative server or a game client.

Phase 6 replaced the single-process hot-seat loop with a real client/server split
(see server.py and client.py) — the server owns the simulation, clients render it.
"""

import argparse

from tankbattle.client import GameClient
from tankbattle.server import GameServer
from tankbattle.settings import DEFAULT_HOST, DEFAULT_PORT


def main() -> None:
    """Parse the command line and start either the server or a client."""
    parser = argparse.ArgumentParser(prog="tankbattle", description="Tank Battle — a networked artillery game.")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    server_parser = subparsers.add_parser("server", help="Run the authoritative game server and wait for 2 players.")
    server_parser.add_argument("--host", default=DEFAULT_HOST)
    server_parser.add_argument("--port", type=int, default=DEFAULT_PORT)

    client_parser = subparsers.add_parser("client", help="Connect to a game server and play.")
    client_parser.add_argument("--host", default=DEFAULT_HOST)
    client_parser.add_argument("--port", type=int, default=DEFAULT_PORT)

    args = parser.parse_args()

    if args.mode == "server":
        GameServer(args.host, args.port).start()
    else:
        GameClient(args.host, args.port).connect()


if __name__ == "__main__":
    main()
