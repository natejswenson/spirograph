import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import math
import pygame
import theme
from utils import draw_card, lerp_color
from constants import PANEL_W, WINDOW_H, CANVAS_X, CANVAS_Y, CANVAS_SIZE


def draw_panel(screen, app, mouse, tick):
    panel = pygame.Surface((PANEL_W, WINDOW_H))
    panel.fill(theme.PANEL)

    # Title bar
    pygame.draw.rect(panel, theme.CARD, pygame.Rect(0, 0, PANEL_W, 44))
    pygame.draw.line(panel, theme.CARD_EDGE, (0, 44), (PANEL_W, 44))
    pulse = 0.5 + 0.5 * math.sin(tick * theme.STATUS_PULSE_FREQ)
    dot_c = lerp_color(theme.STATUS_DOT_IDLE, theme.DRAW, pulse) \
            if app.engine.drawing else theme.STATUS_DOT_IDLE
    pygame.draw.circle(panel, dot_c, (16, 22), theme.STATUS_DOT_R)
    panel.blit(app.fonts["title"].render("SPIROGRAPH STUDIO", True, theme.TEXT), (28, 14))

    # Preview card
    draw_card(panel, app.cards["preview"])
    panel.blit(app.fonts["section"].render("👁  Preview", True, theme.TEXT_DIM),
               (app.cards["preview"].x + 10, app.cards["preview"].y + 8))
    app.preview.update(app.engine.drawing)
    app.preview.draw(panel, app.R(), app.r(), app.d(),
                     app.color_picker.current_solid(), app.fonts)

    # Sliders card
    draw_card(panel, app.cards["sliders"])
    panel.blit(app.fonts["section"].render("🎛  Adjust the Shape", True, theme.TEXT_DIM),
               (app.cards["sliders"].x + 10, app.cards["sliders"].y + 8))
    for s in app.sliders:
        s.draw(panel)

    # Color card
    draw_card(panel, app.cards["color"])
    app.color_picker.draw(panel)

    # Button card
    draw_card(panel, app.cards["buttons"])
    for btn in app.buttons:
        btn.draw(panel, btn.rect.collidepoint(mouse))

    _draw_status(panel, app)
    pygame.draw.line(panel, theme.CARD_EDGE, (PANEL_W - 1, 0), (PANEL_W - 1, WINDOW_H))
    screen.blit(panel, (0, 0))


def _draw_status(panel, app):
    sy = WINDOW_H - 30
    pygame.draw.line(panel, theme.CARD_EDGE, (0, sy), (PANEL_W, sy))
    f = app.fonts["small"]

    if app.engine.drawing:
        pct = app.engine.draw_index / max(app.engine.draw_total, 1)
        bar = pygame.Rect(8, sy + 8, PANEL_W - 16, 6)
        pygame.draw.rect(panel, theme.CARD_EDGE, bar,
                         border_radius=theme.STATUS_PROGRESS_R)
        if pct > 0:
            pygame.draw.rect(panel, theme.DRAW,
                             pygame.Rect(bar.x, bar.y, int(bar.w * pct), bar.h),
                             border_radius=theme.STATUS_PROGRESS_R)
        panel.blit(f.render(f"Drawing…  {int(pct * 100)}%", True, theme.TEXT_DIM),
                   (10, sy + 16))
    elif app.save_flash > 0:
        app.save_flash -= 1
        panel.blit(f.render("✓  Saved to Desktop/spirograph", True, theme.SAVE),
                   (10, sy + 8))
    else:
        panel.blit(f.render(
            f"Layers: {app.engine.layer_count}   Undo: {app.engine.undo_count}",
            True, theme.TEXT_DIM), (10, sy + 8))


def draw_canvas(screen, app):
    screen.fill(theme.BG)
    for offset, alpha in theme.CANVAS_AURA_LAYERS:
        aura = pygame.Surface((CANVAS_SIZE + offset * 2, CANVAS_SIZE + offset * 2),
                              pygame.SRCALPHA)
        col  = theme.DRAW if app.engine.drawing else theme.CANVAS_GLOW_IDLE
        pygame.draw.rect(aura, (*col, alpha), aura.get_rect(),
                         border_radius=10 + offset)
        screen.blit(aura, (CANVAS_X - offset, CANVAS_Y - offset))

    pygame.draw.rect(screen, theme.CARD_EDGE,
                     pygame.Rect(CANVAS_X - 2, CANVAS_Y - 2,
                                 CANVAS_SIZE + 4, CANVAS_SIZE + 4),
                     theme.CANVAS_BORDER_W, border_radius=theme.CANVAS_BORDER_R)
    screen.blit(app.engine.canvas, (CANVAS_X, CANVAS_Y))
