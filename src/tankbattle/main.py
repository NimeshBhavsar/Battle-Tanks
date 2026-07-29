"""Phase 1: open a window, show static terrain, two tanks, and a turn indicator.
Phase 2: move, rotate the barrel, adjust power; moving spends the turn.
Phase 3: fire shells with weight-dependent trajectories; firing spends the turn.
Phase 4: detect hits, apply distance-based damage, and detect game over.
Phase 5: carve craters into the terrain and settle tanks onto the new ground.
"""

import pygame

from tankbattle.engine import collision, damage, terrain_engine
from tankbattle.engine.turn_manager import TurnManager
from tankbattle.models.ammunition import HeavyShell, LightShell, MediumShell
from tankbattle.models.player import Player
from tankbattle.models.tank import Tank
from tankbattle.models.terrain import Terrain
from tankbattle.ui import game_screen
from tankbattle.utils.constants import (
    EXPLOSION_FRAMES,
    FPS,
    PLAYER1_COLOR,
    PLAYER2_COLOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WINDOW_TITLE,
)
from tankbattle.utils.helpers import distance


def build_players(terrain: Terrain) -> list[Player]:
    p1_x, p2_x = SCREEN_WIDTH * 0.15, SCREEN_WIDTH * 0.85
    tank1 = Tank(player_id=1, x=p1_x, y=terrain.height_at(p1_x), color=PLAYER1_COLOR)
    tank2 = Tank(player_id=2, x=p2_x, y=terrain.height_at(p2_x), color=PLAYER2_COLOR)
    tank2.angle = 135.0  # face tank 1
    return [Player(1, "Player 1", tank1), Player(2, "Player 2", tank2)]


def run(headless: bool = False, max_frames: int | None = None) -> None:
    pygame.init()
    flags = pygame.HIDDEN if headless else 0
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 64)

    terrain = Terrain(seed=42)
    players = build_players(terrain)
    turn_manager = TurnManager(players)

    move_keys = (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d)
    ammo_keys = {pygame.K_1: LightShell, pygame.K_2: MediumShell, pygame.K_3: HeavyShell}
    acted_this_turn = False
    active_projectile = None
    explosion_position = None
    explosion_frames_left = 0
    game_over_text = None

    frame_count = 0
    running = True
    while running:
        current_tank = turn_manager.current_player.tank

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif game_over_text is not None:
                continue
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and active_projectile is None and not acted_this_turn:
                    active_projectile = current_tank.fire()
                    acted_this_turn = True
                elif event.key in ammo_keys and active_projectile is None:
                    current_tank.current_ammo = ammo_keys[event.key]()
            elif event.type == pygame.KEYUP and event.key in move_keys and acted_this_turn:
                turn_manager.end_turn()
                acted_this_turn = False

        if game_over_text is None:
            if active_projectile is None:
                keys = pygame.key.get_pressed()
                if current_tank.fuel > 0:
                    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                        current_tank.move(-1, terrain)
                        acted_this_turn = True
                    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                        current_tank.move(1, terrain)
                        acted_this_turn = True

                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    current_tank.rotate_barrel(1)
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    current_tank.rotate_barrel(-1)

                if keys[pygame.K_e]:
                    current_tank.adjust_power(1)
                elif keys[pygame.K_q]:
                    current_tank.adjust_power(-1)
            else:
                active_projectile.update()
                opponents = [p.tank for p in players if p.tank is not current_tank]
                hit_point = collision.check_collision(active_projectile, terrain, opponents)
                if hit_point is not None:
                    blast_radius = active_projectile.blast_radius
                    max_damage = active_projectile.damage
                    explosion_position = active_projectile.explode()
                    explosion_frames_left = EXPLOSION_FRAMES
                    active_projectile = None

                    for player in players:
                        hit_distance = distance(player.tank.position, explosion_position)
                        amount = damage.calculate_damage(hit_distance, blast_radius, max_damage)
                        if amount > 0:
                            player.tank.take_damage(amount)

                    terrain_engine.carve_crater(terrain, *explosion_position, blast_radius)
                    for player in players:
                        tx, _ = player.tank.position
                        player.tank.position = (tx, terrain.height_at(tx))

                    survivors = [p for p in players if p.tank.alive]
                    if len(survivors) <= 1:
                        game_over_text = f"{survivors[0].name} Wins!" if survivors else "Draw!"
                    else:
                        turn_manager.end_turn()
                        acted_this_turn = False

        if explosion_position is not None:
            explosion_frames_left -= 1
            if explosion_frames_left <= 0:
                explosion_position = None

        trajectory = None
        if game_over_text is None and active_projectile is None:
            trajectory = current_tank.preview_trajectory(terrain)

        game_screen.render(
            screen, terrain, players, turn_manager, font,
            projectile=active_projectile, explosion=explosion_position,
            game_over_text=game_over_text, big_font=big_font,
            trajectory=trajectory,
        )
        pygame.display.flip()
        clock.tick(FPS)

        frame_count += 1
        if max_frames is not None and frame_count >= max_frames:
            running = False

    pygame.quit()


def main() -> None:
    run()


if __name__ == "__main__":
    main()
