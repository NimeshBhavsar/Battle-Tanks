"""End-of-match overlay: the winner banner with the match statistics chart underneath."""

import io

import pygame

from tankbattle.utils.constants import WHITE


def load_chart(png_bytes: bytes) -> pygame.Surface:
    """Decode the PNG chart sent by the server into a surface ready to blit."""
    return pygame.image.load(io.BytesIO(png_bytes)).convert()


def draw(
    surface: pygame.Surface,
    chart: pygame.Surface | None,
    font: pygame.font.Font,
    big_font: pygame.font.Font,
    title: str,
) -> None:
    """Dim the battlefield and show the result, the chart (or a wait message) and the key hints."""
    width, height = surface.get_size()
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))

    banner = big_font.render(title, True, WHITE)
    surface.blit(banner, banner.get_rect(midtop=(width // 2, 24)))

    if chart is None:
        wait = font.render("Building match report...", True, WHITE)
        surface.blit(wait, wait.get_rect(center=(width // 2, height // 2)))
    else:
        if chart.get_width() > width - 20:  # window narrower than the chart: shrink to fit
            scale = (width - 20) / chart.get_width()
            chart = pygame.transform.smoothscale(
                chart, (int(chart.get_width() * scale), int(chart.get_height() * scale))
            )
        surface.blit(chart, chart.get_rect(center=(width // 2, height // 2 + 20)))

    hint = font.render("Tab - hide stats     Esc - menu / restart", True, WHITE)
    surface.blit(hint, hint.get_rect(midbottom=(width // 2, height - 16)))
