import math
import pygame
from constants import C_CANVAS_BG, C_CARD, C_CARD_EDGE


def gcd(a, b):
    a, b = int(round(a)), int(round(b))
    while b:
        a, b = b, a % b
    return a


def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def load_fonts():
    pygame.font.init()
    return {
        "title":   pygame.font.SysFont("Arial", 15, bold=True),
        "section": pygame.font.SysFont("Arial", 11, bold=True),
        "label":   pygame.font.SysFont("Arial", 12, bold=True),
        "value":   pygame.font.SysFont("Courier New", 13, bold=True),
        "btn":     pygame.font.SysFont("Arial", 13, bold=True),
        "small":   pygame.font.SysFont("Arial", 11),
    }


def draw_card(surface, rect, color=C_CARD, edge=C_CARD_EDGE, radius=10):
    sh = pygame.Surface((rect.w + 4, rect.h + 5), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 55), sh.get_rect(), border_radius=radius + 2)
    surface.blit(sh, (rect.x - 1, rect.y + 3))
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    pygame.draw.rect(surface, edge,  rect, 1, border_radius=radius)


def make_canvas_bg(size):
    surf = pygame.Surface((size, size))
    surf.fill(C_CANVAS_BG)
    for gx in range(28, size, 28):
        for gy in range(28, size, 28):
            c = 20 + int(7 * math.sin(gx * 0.12) * math.cos(gy * 0.12))
            surf.set_at((gx, gy), (c, c, c + 10))
    return surf
