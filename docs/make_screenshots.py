"""Regenerate the images in docs/screenshots/.

Each scene is drawn by the game's own rendering code (game_screen, hud, menu, effects,
report_view) from a scripted server state, on an off-screen window - so no server, second
player or display is needed. Run from the repository root:

    uv run python docs/make_screenshots.py
"""

import os
import pathlib
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from tankbattle.engine import terrain_engine  # noqa: E402
from tankbattle.engine.turn_manager import TurnManager  # noqa: E402
from tankbattle.models.ammunition import HeavyShell, LightShell, MediumShell  # noqa: E402
from tankbattle.models.projectile import Projectile  # noqa: E402
from tankbattle.models.terrain import Terrain  # noqa: E402
from tankbattle.server import GameServer, build_players  # noqa: E402
from tankbattle.ui import game_screen, menu, report_view  # noqa: E402
from tankbattle.ui.effects import Effects  # noqa: E402
from tankbattle.utils.constants import (  # noqa: E402
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SKY_COLOR,
    TRAJECTORY_VISIBLE_FRACTION,
    WHITE,
)

DOCS = pathlib.Path(__file__).resolve().parent
OUT = DOCS / "screenshots"
OUT.mkdir(exist_ok=True)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 64)


def new_scene() -> GameServer:
    """A fresh match on a fixed terrain, with named players."""
    random.seed(5)
    server = GameServer("127.0.0.1", 0)
    server.terrain = Terrain(seed=4)
    server.players = build_players(server.terrain)
    server.turn_manager = TurnManager(server.players)
    server.players[0].name, server.players[1].name = "Alice", "Bob"
    return server


def can_at(server: GameServer, x: float) -> tuple[float, float]:
    return (x, server.terrain.height_at(x))


def trajectory_of(server: GameServer) -> list[tuple[float, float]]:
    points = server.turn_manager.current_player.tank.preview_trajectory(server.terrain)
    return points[: max(1, int(len(points) * TRAJECTORY_VISIBLE_FRACTION))]


def draw(server: GameServer, name: str, **kwargs) -> None:
    game_screen.render(
        screen, server.terrain, server.players, server.turn_manager, font, big_font=big_font, **kwargs
    )
    save(name)


def zoom(name: str, area: pygame.Rect, factor: int) -> None:
    """Save an enlarged crop of the current screen."""
    crop = screen.subsurface(area.clip(screen.get_rect())).copy()
    size = (crop.get_width() * factor, crop.get_height() * factor)
    pygame.image.save(pygame.transform.scale(crop, size), str(OUT / name))
    print("saved", name)


def save(name: str) -> None:
    pygame.image.save(screen, str(OUT / name))
    print("saved", name)


# 1. Normal gameplay: HUD, fuel cans, aim preview ---------------------------------------------
s = new_scene()
s.players[0].tank.angle, s.players[0].tank.power = 52.0, 70.0
s.players[0].tank.fuel = 62
s.players[1].tank.health = 70
draw(s, "01_gameplay.png", trajectory=trajectory_of(s), fuel_pickups=[can_at(s, 430), can_at(s, 640)])

# 2. Ammo types ---------------------------------------------------------------------------------
panel = pygame.Surface((SCREEN_WIDTH, 300))
panel.fill(SKY_COLOR)
title = big_font.render("Ammunition", True, WHITE)
panel.blit(title, title.get_rect(midtop=(SCREEN_WIDTH // 2, 14)))
for column, (key, shell) in enumerate((("1", LightShell()), ("2", MediumShell()), ("3", HeavyShell()))):
    cx = SCREEN_WIDTH * (column * 2 + 1) // 6
    Projectile((cx, 120), (0, 0), shell.weight, shell.damage, shell.blast_radius).draw(panel)
    pygame.draw.circle(panel, (255, 140, 0), (cx, 120), int(shell.blast_radius), width=2)  # blast radius
    lines = [
        f"[{key}] {shell.name}",
        f"damage {shell.damage}",
        f"blast radius {shell.blast_radius}",
        f"weight {shell.weight}",
    ]
    for row, line in enumerate(lines):
        text = font.render(line, True, WHITE)
        panel.blit(text, text.get_rect(midtop=(cx, 185 + row * 26)))
pygame.image.save(panel, str(OUT / "02_ammo_types.png"))
print("saved 02_ammo_types.png")

# 3. A shell in flight, leaving a smoke trail -------------------------------------------------
s = new_scene()
tank = s.players[0].tank
tank.angle, tank.power, tank.current_ammo = 55.0, 78.0, MediumShell()
shell = tank.fire()
fx = Effects()
for _ in range(20):
    shell.update()
    fx.add_smoke_trail(shell.position, shell.weight)
    fx.update()
draw(s, "03_shell_smoke_trail.png", projectile=shell, effects=fx)

# 4. Impact: debris, smoke, tank flash, floating damage, explosion ring ------------------------
s = new_scene()
target = s.players[1].tank
target.health = 30
impact = (target.position[0], target.position[1] - 10)
fx = Effects()
fx.add_explosion(impact, HeavyShell().blast_radius)
fx.add_hit_flash(2)
for _ in range(5):
    fx.update()
draw(s, "04_impact_effects.png", explosion=impact, explosion_progress=0.3, effects=fx, damage_popups=[(2, 70, 0.15)])
zoom("04b_impact_closeup.png", pygame.Rect(impact[0] - 90, impact[1] - 90, 180, 120), 5)

# 5 & 6. Destructible terrain: before and after a Heavy shell --------------------------------------
s = new_scene()
draw(s, "05_terrain_before.png")
terrain_engine.carve_crater(s.terrain, 512, s.terrain.height_at(512), HeavyShell().blast_radius + 15)
draw(s, "06_terrain_after.png")

# 7. Refuelling: low fuel, can just ahead --------------------------------------------------------
s = new_scene()
s.players[0].tank.position = (300, s.terrain.height_at(300))
s.players[0].tank.fuel = 8
draw(s, "07_fuel_pickup.png", fuel_pickups=[can_at(s, 380), can_at(s, 720)])
zoom("07b_hud_bars.png", pygame.Rect(0, 0, 200, 70), 5)

# 8 & 9. Menu and name editing ----------------------------------------------------------------------
s = new_scene()
draw(s, "08_menu.png")
menu.draw(screen, font, big_font, editing_name=False, name_buffer="", show_restart=False)
save("08_menu.png")
draw(s, "09_edit_name.png")
menu.draw(screen, font, big_font, editing_name=True, name_buffer="Alice", show_restart=False)
save("09_edit_name.png")

# 10. End screen with the match statistics chart (from the bot-vs-bot sample match) ---------------------
s = new_scene()
s.players[1].tank.health = 0
draw(s, "10_end_screen.png", game_over_text="Alice Wins!")
chart = report_view.load_chart((DOCS / "sample_match.png").read_bytes())
report_view.draw(screen, chart, font, big_font, "Alice Wins!")
save("10_end_screen.png")
