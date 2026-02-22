import math
import pygame
from utils import draw_card, lerp_color
from constants import (
    PANEL_W, WINDOW_H, CANVAS_X, CANVAS_Y, CANVAS_SIZE,
    C_BG, C_PANEL, C_CARD, C_CARD_EDGE, C_TEXT_DIM, C_DRAW, C_SAVE,
)


def draw_panel(screen, app, mouse, tick):
    panel = pygame.Surface((PANEL_W, WINDOW_H))
    panel.fill(C_PANEL)

    # Title bar
    pygame.draw.rect(panel, C_CARD, pygame.Rect(0, 0, PANEL_W, 44))
    pygame.draw.line(panel, C_CARD_EDGE, (0, 44), (PANEL_W, 44))
    pulse = 0.5 + 0.5 * math.sin(tick * 0.07)
    dot_c = lerp_color((70, 65, 110), C_DRAW, pulse) if app.engine.drawing else (55, 50, 88)
    pygame.draw.circle(panel, dot_c, (16, 22), 6)
    panel.blit(app.fonts["title"].render("SPIROGRAPH STUDIO", True, (235, 232, 255)), (28, 14))

    # Preview card
    draw_card(panel, app.cards["preview"])
    panel.blit(app.fonts["section"].render("👁  Preview", True, C_TEXT_DIM),
               (app.cards["preview"].x + 10, app.cards["preview"].y + 8))
    app.preview.update(app.engine.drawing)
    app.preview.draw(panel, app._R(), app._r(), app._d(),
                     app.color_picker.current_solid(), app.fonts)

    # Sliders card
    draw_card(panel, app.cards["sliders"])
    panel.blit(app.fonts["section"].render("🎛  Adjust the Shape", True, C_TEXT_DIM),
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

    # Status strip
    _draw_status(panel, app, tick)

    pygame.draw.line(panel, C_CARD_EDGE, (PANEL_W - 1, 0), (PANEL_W - 1, WINDOW_H))
    screen.blit(panel, (0, 0))


def _draw_status(panel, app, tick):
    sy = WINDOW_H - 30
    pygame.draw.line(panel, C_CARD_EDGE, (0, sy), (PANEL_W, sy))
    f = app.fonts["small"]

    if app.engine.drawing:
        pct = app.engine.draw_index / max(app.engine.draw_total, 1)
        bar = pygame.Rect(8, sy + 8, PANEL_W - 16, 6)
        pygame.draw.rect(panel, C_CARD_EDGE, bar, border_radius=3)
        if pct > 0:
            pygame.draw.rect(panel, C_DRAW,
                             pygame.Rect(bar.x, bar.y, int(bar.w * pct), bar.h),
                             border_radius=3)
        panel.blit(f.render(f"Drawing…  {int(pct * 100)}%", True, C_TEXT_DIM), (10, sy + 16))
    elif app.save_flash > 0:
        app.save_flash -= 1
        panel.blit(f.render("✓  Saved to Desktop/spirograph", True, C_SAVE), (10, sy + 8))
    else:
        panel.blit(f.render(
            f"Layers: {app.engine.layer_count}   Undo: {app.engine.undo_count}",
            True, C_TEXT_DIM), (10, sy + 8))


def draw_canvas(screen, app):
    screen.fill(C_BG)
    for offset, alpha in ((16, 12), (9, 28), (3, 50)):
        aura = pygame.Surface((CANVAS_SIZE + offset * 2, CANVAS_SIZE + offset * 2),
                              pygame.SRCALPHA)
        col  = C_DRAW if app.engine.drawing else (48, 44, 88)
        pygame.draw.rect(aura, (*col, alpha), aura.get_rect(),
                         border_radius=10 + offset)
        screen.blit(aura, (CANVAS_X - offset, CANVAS_Y - offset))

    pygame.draw.rect(screen, C_CARD_EDGE,
                     pygame.Rect(CANVAS_X - 2, CANVAS_Y - 2,
                                 CANVAS_SIZE + 4, CANVAS_SIZE + 4),
                     2, border_radius=6)
    screen.blit(app.engine.canvas, (CANVAS_X, CANVAS_Y))
