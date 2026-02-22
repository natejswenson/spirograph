import pygame
import theme
from constants import PANEL_W, PREVIEW_SIZE
from preview import PreviewWidget
from widgets import Slider, Button, ColorPicker


def build_ui(fonts):
    """Build and return all UI widgets and card rects as a dict."""
    px = 16
    sw = PANEL_W - px * 2 - 12

    # ── Preview card ──────────────────────────────────────────────────────────
    preview_card_y = 48
    preview_card_h = PREVIEW_SIZE + 22
    pw_x = (PANEL_W - PREVIEW_SIZE) // 2
    pw_y = preview_card_y + 11
    preview = PreviewWidget(pw_x, pw_y, PREVIEW_SIZE)

    # ── Sliders ───────────────────────────────────────────────────────────────
    sliders_card_y = preview_card_y + preview_card_h + 6
    y = sliders_card_y + 24
    slider_defs = [
        ("⭕", "Big Circle",   50, 300, 150, theme.SLIDER_COLORS[0]),
        ("🔵", "Little Wheel",  5, 200,  80, theme.SLIDER_COLORS[1]),
        ("✏️", "Pen Reach",     5, 250, 100, theme.SLIDER_COLORS[2]),
        ("⚡", "Speed",         1,  20,   5, theme.SLIDER_COLORS[3]),
        ("📏", "Line Width",    1,   8,   1, theme.SLIDER_COLORS[4]),
    ]
    sliders = []
    for em, lb, mn, mx, init, col in slider_defs:
        sliders.append(Slider(px, y, sw, mn, mx, init, em, lb, col, fonts))
        y += Slider.ROW_H
    sliders_card_h = y - sliders_card_y + 8

    # ── Color picker ──────────────────────────────────────────────────────────
    color_card_y = sliders_card_y + sliders_card_h + 6
    color_picker = ColorPicker(px, color_card_y + 26, fonts)
    color_card_h = ColorPicker.SW + 40

    # ── Buttons ───────────────────────────────────────────────────────────────
    btn_card_y = color_card_y + color_card_h + 6
    by  = btn_card_y + 8
    bw  = PANEL_W - 6 - px * 2 + 4
    bh  = 33
    bh2 = (bw - 6) // 2
    btn_draw  = Button(px,           by, bw,  bh, "▶", "Draw",     theme.DRAW,  fonts); by += bh + 6
    btn_undo  = Button(px,           by, bh2, bh, "↩", "Undo",    theme.UNDO,  fonts)
    btn_clear = Button(px + bh2 + 6, by, bh2, bh, "✕", "Clear",   theme.CLEAR, fonts); by += bh + 6
    btn_save  = Button(px,           by, bw,  bh, "💾", "Save PNG", theme.SAVE, fonts); by += bh + 6

    cards = {
        "preview": pygame.Rect(6, preview_card_y, PANEL_W - 6, preview_card_h),
        "sliders": pygame.Rect(6, sliders_card_y, PANEL_W - 6, sliders_card_h),
        "color":   pygame.Rect(6, color_card_y,   PANEL_W - 6, color_card_h),
        "buttons": pygame.Rect(6, btn_card_y,      PANEL_W - 6, by - btn_card_y),
    }

    return {
        "preview":      preview,
        "sliders":      sliders,
        "color_picker": color_picker,
        "buttons":      [btn_draw, btn_undo, btn_clear, btn_save],
        "cards":        cards,
    }
