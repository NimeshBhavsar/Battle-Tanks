"""Pause/restart menu overlay: edit your name, restart after a match ends, or close."""

import pygame

from tankbattle.utils.constants import BLACK, MENU_HIGHLIGHT_COLOR, WHITE


def draw(
    surface: pygame.Surface,
    font: pygame.font.Font,
    big_font: pygame.font.Font,
    *,
    editing_name: bool,
    name_buffer: str,
    show_restart: bool,
) -> None:
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))

    center_x, center_y = surface.get_width() // 2, surface.get_height() // 2

    if editing_name:
        title = big_font.render("Edit Name", True, WHITE)
        surface.blit(title, title.get_rect(center=(center_x, center_y - 60)))

        box = pygame.Rect(0, 0, 320, 44)
        box.center = (center_x, center_y)
        pygame.draw.rect(surface, WHITE, box, border_radius=6)
        pygame.draw.rect(surface, MENU_HIGHLIGHT_COLOR, box, width=2, border_radius=6)
        name_text = font.render(name_buffer + "|", True, BLACK)
        surface.blit(name_text, name_text.get_rect(midleft=(box.left + 12, box.centery)))

        hint = font.render("Enter to confirm — Esc to cancel", True, WHITE)
        surface.blit(hint, hint.get_rect(center=(center_x, center_y + 50)))
        return

    title = big_font.render("Menu", True, WHITE)
    surface.blit(title, title.get_rect(center=(center_x, center_y - 70)))

    options = ["N — Edit Name"]
    if show_restart:
        options.append("R — Restart Match")
    options.append("Esc — Close")

    for index, option in enumerate(options):
        text = font.render(option, True, WHITE)
        surface.blit(text, text.get_rect(center=(center_x, center_y - 10 + index * 32)))
