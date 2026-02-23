import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import math
import pygame
import theme


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
        "title":   pygame.font.SysFont(theme.FONT_FACE_DEFAULT, theme.FONT_SIZE_TITLE,   bold=True),
        "section": pygame.font.SysFont(theme.FONT_FACE_DEFAULT, theme.FONT_SIZE_SECTION, bold=True),
        "label":   pygame.font.SysFont(theme.FONT_FACE_DEFAULT, theme.FONT_SIZE_LABEL,   bold=True),
        "value":   pygame.font.SysFont(theme.FONT_FACE_MONO,    theme.FONT_SIZE_VALUE,   bold=True),
        "btn":     pygame.font.SysFont(theme.FONT_FACE_DEFAULT, theme.FONT_SIZE_BTN,     bold=True),
        "small":   pygame.font.SysFont(theme.FONT_FACE_DEFAULT, theme.FONT_SIZE_SMALL),
    }


def draw_card(surface, rect,
              color=None, edge=None,
              radius=None):
    color  = color  or theme.CARD
    edge   = edge   or theme.CARD_EDGE
    radius = radius or theme.CARD_RADIUS
    sh = pygame.Surface((rect.w + 4, rect.h + 5), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, theme.CARD_SHADOW_A),
                     sh.get_rect(), border_radius=radius + 2)
    surface.blit(sh, (rect.x - 1, rect.y + 3))
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    pygame.draw.rect(surface, edge,  rect, 1, border_radius=radius)


def make_canvas_bg(size):
    surf = pygame.Surface((size, size))
    surf.fill(theme.CANVAS_BG)
    sp, base, amp, freq, tint = (
        theme.GRID_SPACING, theme.GRID_BASE_BRIGHT,
        theme.GRID_VARY_AMP, theme.GRID_VARY_FREQ, theme.GRID_BLUE_TINT,
    )
    for gx in range(sp, size, sp):
        for gy in range(sp, size, sp):
            c = base + int(amp * math.sin(gx * freq) * math.cos(gy * freq))
            surf.set_at((gx, gy), (c, c, c + tint))
    return surf
