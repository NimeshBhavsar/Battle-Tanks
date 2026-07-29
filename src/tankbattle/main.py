"""Phase 1: open a window, show static terrain, two tanks, and a turn indicator.
Phase 2: move, rotate the barrel, adjust power; moving spends the turn.
"""

import pygame

from tankbattle.engine.turn_manager import TurnManager
from tankbattle.models.player import Player
from tankbattle.models.tank import Tank
from tankbattle.models.terrain import Terrain
from tankbattle.ui import game_screen
from tankbattle.utils.constants import FPS, PLAYER1_COLOR, PLAYER2_COLOR, SCREEN_HEIGHT, SCREEN_WIDTH, WINDOW_TITLE


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

    terrain = Terrain(seed=42)
    players = build_players(terrain)
    turn_manager = TurnManager(players)

    move_keys = (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d)
    moved_this_turn = False

    frame_count = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                turn_manager.end_turn()
                moved_this_turn = False
            elif event.type == pygame.KEYUP and event.key in move_keys and moved_this_turn:
                turn_manager.end_turn()
                moved_this_turn = False

        keys = pygame.key.get_pressed()
        current_tank = turn_manager.current_player.tank

        if current_tank.fuel > 0:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                current_tank.move(-1, terrain)
                moved_this_turn = True
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                current_tank.move(1, terrain)
                moved_this_turn = True

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            current_tank.rotate_barrel(1)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            current_tank.rotate_barrel(-1)

        if keys[pygame.K_e]:
            current_tank.adjust_power(1)
        elif keys[pygame.K_q]:
            current_tank.adjust_power(-1)

        game_screen.render(screen, terrain, players, turn_manager, font)
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
