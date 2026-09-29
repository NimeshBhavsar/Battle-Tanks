"""Authoritative game server: owns physics, collision, damage, terrain, and turn state.

Two clients connect, each is assigned a player_id (1 or 2). Every tick the server reads
the current player's latest input, advances the simulation, and broadcasts a full state
snapshot to both clients. The server never renders anything itself.
"""

import random
import socket
import threading
import time

from tankbattle import network
from tankbattle.engine import collision, damage, terrain_engine
from tankbattle.engine.turn_manager import TurnManager
from tankbattle.models.ammunition import AMMO_BY_NAME
from tankbattle.models.player import Player
from tankbattle.models.tank import Tank
from tankbattle.models.terrain import Terrain
from tankbattle.settings import TANK_START_FUEL
from tankbattle.utils.constants import (
    EXPLOSION_FRAMES,
    FPS,
    FUEL_PICKUP_EDGE_MARGIN,
    FUEL_PICKUP_MAX,
    FUEL_PICKUP_MIN_TANK_DISTANCE,
    FUEL_PICKUP_REFILL,
    FUEL_PICKUP_START,
    FUEL_PICKUP_WIDTH,
    MAX_NAME_LENGTH,
    PLAYER1_COLOR,
    PLAYER2_COLOR,
    SCREEN_WIDTH,
    TANK_WIDTH,
)
from tankbattle.utils.helpers import clamp, distance

_EMPTY_INPUT = {"move": 0, "rotate": 0, "power": 0, "fire": False, "ammo": None, "restart": False, "name": None}


def build_players(terrain: Terrain) -> list[Player]:
    """Create both players, with tanks placed on the terrain near opposite edges."""
    p1_x, p2_x = SCREEN_WIDTH * 0.15, SCREEN_WIDTH * 0.85
    tank1 = Tank(player_id=1, x=p1_x, y=terrain.height_at(p1_x), color=PLAYER1_COLOR)
    tank2 = Tank(player_id=2, x=p2_x, y=terrain.height_at(p2_x), color=PLAYER2_COLOR)
    tank2.angle = 135.0  # face tank 1
    return [Player(1, "Player 1", tank1), Player(2, "Player 2", tank2)]


class GameServer:
    """Authoritative server: simulates the match and broadcasts its state to both clients."""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

        self.terrain = Terrain()  # random seed: a new match gets new terrain
        self.players = build_players(self.terrain)
        self.turn_manager = TurnManager(self.players)

        self.acted_this_turn = False
        self.was_moving = False
        self.active_projectile = None
        self.explosion_position: tuple[float, float] | None = None
        self.explosion_frames_left = 0
        self.game_over_text: str | None = None
        self.fuel_pickups: list[float] = []  # x positions; y is derived from the terrain
        for _ in range(FUEL_PICKUP_START):
            self._spawn_fuel_pickup()

        self.lock = threading.Lock()
        self.client_sockets: dict[int, socket.socket] = {}
        self.pending_inputs: dict[int, dict] = {}

    def start(self) -> None:
        """Wait for two players to connect, then run the game loop forever."""
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.host, self.port))
        server_sock.listen(2)
        print(f"Waiting for 2 players on {self.host}:{self.port}...")

        for player_id in (1, 2):
            conn, addr = server_sock.accept()
            with self.lock:
                self.client_sockets[player_id] = conn
            network.send_message(conn, {"type": "welcome", "player_id": player_id})
            threading.Thread(target=self._receive_loop, args=(player_id, conn), daemon=True).start()
            print(f"Player {player_id} connected from {addr}")

        print("Both players connected — starting match")
        self._run_game_loop()

    def _receive_loop(self, player_id: int, conn: socket.socket) -> None:
        while True:
            message = network.receive_message(conn)
            if message is None:
                break
            with self.lock:
                self.pending_inputs[player_id] = message

    def _run_game_loop(self) -> None:
        tick_interval = 1.0 / FPS
        while True:
            start_time = time.monotonic()
            self._tick()
            self._broadcast_state()
            elapsed = time.monotonic() - start_time
            remaining = tick_interval - elapsed
            if remaining > 0:
                time.sleep(remaining)

    def _tick(self) -> None:
        with self.lock:
            self._apply_name_changes_locked()

            current_player = self.turn_manager.current_player
            input_state = dict(self.pending_inputs.get(current_player.player_id, _EMPTY_INPUT))
            # One-shot fields are consumed here so a client gone quiet right after
            # firing/switching ammo can't have that same message replayed next tick.
            cached = self.pending_inputs.get(current_player.player_id)
            if cached is not None:
                cached["fire"] = False
                cached["ammo"] = None

            restart_requested = False
            if self.game_over_text is not None:
                restart_requested = any(inp.get("restart") for inp in self.pending_inputs.values())
                if restart_requested:
                    for inp in self.pending_inputs.values():
                        inp["restart"] = False

        if self.game_over_text is not None:
            if restart_requested:
                self._reset_match()
            return

        current_tank = current_player.tank

        if self.active_projectile is None:
            self._apply_input(current_tank, input_state)
        else:
            self._advance_projectile(current_tank)

        if self.explosion_position is not None:
            self.explosion_frames_left -= 1
            if self.explosion_frames_left <= 0:
                self.explosion_position = None

    def _apply_name_changes_locked(self) -> None:
        """Rename lands immediately, regardless of whose turn it is. Caller must hold self.lock."""
        for player_id, input_state in self.pending_inputs.items():
            new_name = input_state.get("name")
            if not new_name:
                continue
            cleaned = new_name.strip()[:MAX_NAME_LENGTH]
            if cleaned:
                for player in self.players:
                    if player.player_id == player_id:
                        player.name = cleaned
                        break
            input_state["name"] = None

    def _apply_input(self, current_tank: Tank, input_state: dict) -> None:
        move_dir = input_state.get("move", 0)
        if move_dir != 0 and current_tank.fuel > 0:
            current_tank.move(move_dir, self.terrain)
            self._collect_fuel_pickups(current_tank)
            self.acted_this_turn = True
            self.was_moving = True
        elif self.was_moving and move_dir == 0 and self.acted_this_turn:
            self._end_turn()
            self.acted_this_turn = False
            self.was_moving = False

        rotate_dir = input_state.get("rotate", 0)
        if rotate_dir != 0:
            current_tank.rotate_barrel(rotate_dir)

        power_dir = input_state.get("power", 0)
        if power_dir != 0:
            current_tank.adjust_power(power_dir)

        ammo_name = input_state.get("ammo")
        if ammo_name in AMMO_BY_NAME:
            current_tank.current_ammo = AMMO_BY_NAME[ammo_name]()

        if input_state.get("fire") and not self.acted_this_turn:
            self.active_projectile = current_tank.fire()
            self.acted_this_turn = True

    def _advance_projectile(self, current_tank: Tank) -> None:
        self.active_projectile.update()
        opponents = [p.tank for p in self.players if p.tank is not current_tank]
        hit_point = collision.check_collision(self.active_projectile, self.terrain, opponents)
        if hit_point is None:
            return

        blast_radius = self.active_projectile.blast_radius
        max_damage = self.active_projectile.damage
        self.explosion_position = self.active_projectile.explode()
        self.explosion_frames_left = EXPLOSION_FRAMES
        self.active_projectile = None

        for player in self.players:
            hit_distance = distance(player.tank.position, self.explosion_position)
            amount = damage.calculate_damage(hit_distance, blast_radius, max_damage)
            if amount > 0:
                player.tank.take_damage(amount)

        terrain_engine.carve_crater(self.terrain, *self.explosion_position, blast_radius)
        for player in self.players:
            tx, _ = player.tank.position
            player.tank.position = (tx, self.terrain.height_at(tx))

        survivors = [p for p in self.players if p.tank.alive]
        if len(survivors) <= 1:
            self.game_over_text = f"{survivors[0].name} Wins!" if survivors else "Draw!"
        else:
            self._end_turn()
            self.acted_this_turn = False

    def _end_turn(self) -> None:
        self.turn_manager.end_turn()
        if len(self.fuel_pickups) < FUEL_PICKUP_MAX:
            self._spawn_fuel_pickup()

    def _spawn_fuel_pickup(self) -> None:
        """Drop a can at a random x, away from tanks and other cans. Gives up quietly if the map is crowded."""
        tank_xs = [p.tank.position[0] for p in self.players]
        for _ in range(20):
            x = random.uniform(FUEL_PICKUP_EDGE_MARGIN, self.terrain.width - FUEL_PICKUP_EDGE_MARGIN)
            if all(abs(x - other) >= FUEL_PICKUP_MIN_TANK_DISTANCE for other in tank_xs + self.fuel_pickups):
                self.fuel_pickups.append(x)
                return

    def _collect_fuel_pickups(self, tank: Tank) -> None:
        reach = TANK_WIDTH / 2 + FUEL_PICKUP_WIDTH / 2
        remaining = [x for x in self.fuel_pickups if abs(x - tank.position[0]) > reach]
        collected = len(self.fuel_pickups) - len(remaining)
        if collected:
            self.fuel_pickups = remaining
            tank.fuel = clamp(tank.fuel + collected * FUEL_PICKUP_REFILL, 0, TANK_START_FUEL)

    def _reset_match(self) -> None:
        self.terrain = Terrain()
        self.players = build_players(self.terrain)
        self.turn_manager = TurnManager(self.players)
        self.acted_this_turn = False
        self.was_moving = False
        self.active_projectile = None
        self.explosion_position = None
        self.explosion_frames_left = 0
        self.game_over_text = None
        self.fuel_pickups = []
        for _ in range(FUEL_PICKUP_START):
            self._spawn_fuel_pickup()
        print("Match restarted")

    def _snapshot(self) -> dict:
        return {
            "type": "state",
            "terrain": list(self.terrain.height_map),
            "tanks": [
                {
                    "player_id": p.player_id,
                    "name": p.name,
                    "position": list(p.tank.position),
                    "angle": p.tank.angle,
                    "power": p.tank.power,
                    "health": p.tank.health,
                    "fuel": p.tank.fuel,
                    "ammo": p.tank.current_ammo.name,
                    "color": list(p.tank.color),
                }
                for p in self.players
            ],
            "current_player_id": self.turn_manager.current_player.player_id,
            "projectile": (
                {"position": list(self.active_projectile.position), "weight": self.active_projectile.weight}
                if self.active_projectile
                else None
            ),
            "explosion": list(self.explosion_position) if self.explosion_position else None,
            "fuel_pickups": [[x, self.terrain.height_at(x)] for x in self.fuel_pickups],
            "game_over_text": self.game_over_text,
        }

    def _broadcast_state(self) -> None:
        snapshot = self._snapshot()
        with self.lock:
            sockets = list(self.client_sockets.items())
        for player_id, sock in sockets:
            try:
                network.send_message(sock, snapshot)
            except OSError:
                print(f"Player {player_id} disconnected")
                with self.lock:
                    self.client_sockets.pop(player_id, None)
