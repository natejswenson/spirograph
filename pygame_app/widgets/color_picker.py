import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))))

import colorsys
import pygame
import theme


class ColorPicker:
    SW  = 26
    GAP = 6

    def __init__(self, x, y, fonts):
        self.x        = x
        self.y        = y
        self.selected = 0
        self.rainbow  = False
        self.fonts    = fonts
        self._build()

    def _build(self):
        self.rects = [
            pygame.Rect(self.x + i * (self.SW + self.GAP), self.y, self.SW, self.SW)
            for i in range(len(theme.PRESET_COLORS))
        ]
        rb_y = self.y + self.SW + 10
        self.rb_rect = pygame.Rect(self.x, rb_y, 16, 16)
        self.rb_pos  = (self.x + 22, rb_y + 1)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self.rects):
                if r.collidepoint(event.pos):
                    self.selected = i
                    self.rainbow  = False
                    return True
            if self.rb_rect.collidepoint(event.pos):
                self.rainbow = not self.rainbow
                return True
        return False

    def get_color(self, idx, total):
        if self.rainbow:
            h = (idx / max(total, 1)) % 1.0
            r, g, b = colorsys.hsv_to_rgb(h, 1.0, 1.0)
            return (int(r * 255), int(g * 255), int(b * 255))
        return theme.PRESET_COLORS[self.selected]

    def current_solid(self):
        return theme.PRESET_COLORS[self.selected]

    def draw(self, surface):
        f = self.fonts
        surface.blit(f["section"].render("🎨  Color", True, theme.TEXT_DIM),
                     (self.x, self.y - 18))

        for i, (r, col) in enumerate(zip(self.rects, theme.PRESET_COLORS)):
            if i == self.selected and not self.rainbow:
                sel = r.inflate(theme.SWATCH_SEL_EXPAND, theme.SWATCH_SEL_EXPAND)
                pygame.draw.rect(surface, col, sel, border_radius=theme.SWATCH_SEL_RADIUS)
            pygame.draw.rect(surface, col, r, border_radius=theme.SWATCH_RADIUS)

        rb_col = theme.RAINBOW_ACTIVE_COLOR if self.rainbow else theme.CARD_EDGE
        pygame.draw.rect(surface, rb_col,       self.rb_rect, border_radius=3)
        pygame.draw.rect(surface, theme.TEXT_DIM, self.rb_rect, 1, border_radius=3)
        if self.rainbow:
            ck = f["small"].render("✓", True, theme.RAINBOW_CHECK_COLOR)
            surface.blit(ck, ck.get_rect(center=self.rb_rect.center))
        rb_label_col = theme.RAINBOW_ACTIVE_COLOR if self.rainbow else theme.TEXT_DIM
        surface.blit(f["label"].render("🌈  Rainbow!", True, rb_label_col), self.rb_pos)
