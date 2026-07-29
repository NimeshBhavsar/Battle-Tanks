"""Phase 1: open a window, show static terrain, two tanks, and a turn indicator."""

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

    frame_count = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                turn_manager.end_turn()

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
