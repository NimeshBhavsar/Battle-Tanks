"""Networked client: renders the state broadcast by the server and sends local input.

The client never simulates the game itself — it mirrors whatever the server last
broadcast (terrain, tanks, projectile, turn) and sends its own held keys/actions
every frame. The server decides what actually happens.
"""

import socket
import threading

import pygame

from tankbattle import network
from tankbattle.engine.turn_manager import TurnManager
from tankbattle.models.ammunition import AMMO_BY_NAME
from tankbattle.models.player import Player
from tankbattle.models.projectile import Projectile
from tankbattle.models.tank import Tank
from tankbattle.models.terrain import Terrain
from tankbattle.ui import game_screen, hud, menu
from tankbattle.ui import sound as sfx
from tankbattle.utils.constants import (
    DAMAGE_POPUP_FRAMES,
    EXPLOSION_FRAMES,
    FPS,
    MAX_NAME_LENGTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SKY_COLOR,
    TRAJECTORY_VISIBLE_FRACTION,
    WINDOW_TITLE,
)


class GameClient:
    """Connects to the server, mirrors its state on screen and forwards local input."""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.player_id: int | None = None
        self.sock: socket.socket | None = None

        self.lock = threading.Lock()
        self.latest_state: dict | None = None

        self.terrain = Terrain(seed=0)  # overwritten by the first state broadcast
        self.tanks_by_id: dict[int, Tank] = {}
        self.players: list[Player] = []
        self.turn_manager: TurnManager | None = None

        self.sounds: dict = {}
        self._had_projectile = False
        self._explosion_last_pos: tuple[float, float] | None = None
        self._explosion_elapsed = 0
        self._last_damage_id: int | None = None  # None until the first state, so a late joiner skips old hits
        self._damage_popups: list[dict] = []

        self.menu_open = False
        self.editing_name = False
        self.name_buffer = ""

    def connect(self) -> None:
        """Connect to the server, wait for the welcome message and run the render loop until the window closes."""
        self.sock = socket.create_connection((self.host, self.port))
        welcome = network.receive_message(self.sock)
        self.player_id = welcome["player_id"]
        threading.Thread(target=self._receive_loop, daemon=True).start()
        self._run_render_loop()

    def _receive_loop(self) -> None:
        while True:
            message = network.receive_message(self.sock)
            if message is None:
                break
            if message.get("type") == "state":
                with self.lock:
                    self.latest_state = message

    def _apply_state(self, state: dict) -> None:
        """Mirror a server state broadcast onto local render-only objects."""
        self.terrain.height_map = list(state["terrain"])

        for tank_data in state["tanks"]:
            player_id = tank_data["player_id"]
            tank = self.tanks_by_id.get(player_id)
            if tank is None:
                tank = Tank(player_id, tank_data["position"][0], tank_data["position"][1], tuple(tank_data["color"]))
                self.tanks_by_id[player_id] = tank
                self.players.append(Player(player_id, tank_data["name"], tank))
            for player in self.players:
                if player.player_id == player_id:
                    player.name = tank_data["name"]
                    break
            tank.position = tuple(tank_data["position"])
            tank.angle = tank_data["angle"]
            tank.power = tank_data["power"]
            tank.health = tank_data["health"]
            tank.fuel = tank_data["fuel"]
            tank.current_ammo = AMMO_BY_NAME[tank_data["ammo"]]()

        if self.turn_manager is None and len(self.players) == 2:
            self.players.sort(key=lambda p: p.player_id)
            self.turn_manager = TurnManager(self.players)

        if self.turn_manager is not None:
            self.turn_manager.set_current(state["current_player_id"])

    def _update_damage_popups(self, events: list[dict]) -> None:
        """Age the floating damage numbers and start one for every hit we haven't shown yet."""
        for popup in self._damage_popups:
            popup["age"] += 1
        self._damage_popups = [p for p in self._damage_popups if p["age"] < DAMAGE_POPUP_FRAMES]

        newest = max((e["id"] for e in events), default=0)
        if self._last_damage_id is not None:
            for event in events:
                if event["id"] > self._last_damage_id:
                    self._damage_popups.append({"player_id": event["player_id"], "amount": event["amount"], "age": 0})
        self._last_damage_id = max(newest, self._last_damage_id or 0)

    def _run_render_loop(self) -> None:
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f"{WINDOW_TITLE} — Player {self.player_id}")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont(None, 28)
        big_font = pygame.font.SysFont(None, 64)
        self.sounds = sfx.load_sounds()

        running = True
        while running:
            fire = False
            ammo = None
            restart = False
            name_to_send = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type != pygame.KEYDOWN:
                    continue
                elif self.editing_name:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        candidate = self.name_buffer.strip()
                        if candidate:
                            name_to_send = candidate
                        self.editing_name = False
                        self.menu_open = False
                    elif event.key == pygame.K_ESCAPE:
                        self.editing_name = False  # cancel, stay in the menu
                    elif event.key == pygame.K_BACKSPACE:
                        self.name_buffer = self.name_buffer[:-1]
                    elif event.unicode.isprintable() and len(self.name_buffer) < MAX_NAME_LENGTH:
                        self.name_buffer += event.unicode
                elif self.menu_open:
                    if event.key == pygame.K_ESCAPE:
                        self.menu_open = False
                    elif event.key == pygame.K_n:
                        self.editing_name = True
                        current_name = next(
                            (p.name for p in self.players if p.player_id == self.player_id),
                            f"Player {self.player_id}",
                        )
                        self.name_buffer = current_name
                    elif event.key == pygame.K_r:
                        restart = True
                        self.menu_open = False
                else:
                    if event.key == pygame.K_ESCAPE:
                        self.menu_open = True
                    elif event.key == pygame.K_SPACE:
                        fire = True
                    elif event.key == pygame.K_1:
                        ammo = "Light"
                    elif event.key == pygame.K_2:
                        ammo = "Medium"
                    elif event.key == pygame.K_3:
                        ammo = "Heavy"

            if self.menu_open:
                move = rotate = power_dir = 0
            else:
                keys = pygame.key.get_pressed()
                left, right = keys[pygame.K_LEFT] or keys[pygame.K_a], keys[pygame.K_RIGHT] or keys[pygame.K_d]
                up, down = keys[pygame.K_UP] or keys[pygame.K_w], keys[pygame.K_DOWN] or keys[pygame.K_s]
                move = -1 if left else 1 if right else 0
                rotate = 1 if up else -1 if down else 0
                power_dir = 1 if keys[pygame.K_e] else -1 if keys[pygame.K_q] else 0

            try:
                network.send_message(
                    self.sock,
                    {
                        "move": move,
                        "rotate": rotate,
                        "power": power_dir,
                        "fire": fire,
                        "ammo": ammo,
                        "restart": restart,
                        "name": name_to_send,
                    },
                )
            except OSError:
                running = False
                break

            with self.lock:
                state = self.latest_state

            game_over_text = None

            if state is None:
                screen.fill(SKY_COLOR)
                hud.draw_message(screen, font, "Waiting for opponent...")
            else:
                self._apply_state(state)

                has_projectile_now = bool(state.get("projectile"))
                if has_projectile_now and not self._had_projectile:
                    sfx.play(self.sounds, "fire")
                self._had_projectile = has_projectile_now

                projectile = None
                if has_projectile_now:
                    proj_data = state["projectile"]
                    projectile = Projectile(tuple(proj_data["position"]), (0.0, 0.0), proj_data.get("weight", 1), 0, 0)

                explosion = tuple(state["explosion"]) if state.get("explosion") else None
                if explosion is None:
                    self._explosion_last_pos = None
                    self._explosion_elapsed = 0
                elif explosion != self._explosion_last_pos:
                    self._explosion_last_pos = explosion
                    self._explosion_elapsed = 0
                    sfx.play(self.sounds, "explosion")
                else:
                    self._explosion_elapsed += 1
                explosion_progress = self._explosion_elapsed / EXPLOSION_FRAMES

                game_over_text = state.get("game_over_text")

                self._update_damage_popups(state.get("damage_events", []))

                trajectory = None
                is_my_turn = self.turn_manager.current_player.player_id == self.player_id
                if game_over_text is None and projectile is None and is_my_turn and not self.menu_open:
                    full_trajectory = self.tanks_by_id[self.player_id].preview_trajectory(self.terrain)
                    trajectory = full_trajectory[: max(1, int(len(full_trajectory) * TRAJECTORY_VISIBLE_FRACTION))]

                game_screen.render(
                    screen,
                    self.terrain,
                    self.players,
                    self.turn_manager,
                    font,
                    projectile=projectile,
                    explosion=explosion,
                    explosion_progress=explosion_progress,
                    game_over_text=game_over_text,
                    big_font=big_font,
                    trajectory=trajectory,
                    fuel_pickups=[tuple(p) for p in state.get("fuel_pickups", [])],
                    damage_popups=[
                        (popup["player_id"], popup["amount"], popup["age"] / DAMAGE_POPUP_FRAMES)
                        for popup in self._damage_popups
                    ],
                )

            if self.menu_open or self.editing_name:
                menu.draw(
                    screen,
                    font,
                    big_font,
                    editing_name=self.editing_name,
                    name_buffer=self.name_buffer,
                    show_restart=game_over_text is not None,
                )

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
