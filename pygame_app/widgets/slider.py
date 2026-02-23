import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))))

import math
import pygame
import theme
from utils import clamp


class Slider:
    TRACK_H  = theme.SLIDER_TRACK_H
    HANDLE_R = theme.SLIDER_HANDLE_R
    ROW_H    = theme.SLIDER_ROW_H

    def __init__(self, x, y, w, mn, mx, init, emoji, label, color, fonts):
        self.track    = pygame.Rect(x, y + 30, w, self.TRACK_H)
        self.min_val  = mn
        self.max_val  = mx
        self._value   = float(init)
        self.emoji    = emoji
        self.label    = label
        self.color    = color
        self.fonts    = fonts
        self.dragging = False

    @property
    def value(self):
        return int(round(self._value))

    def _vx(self, val):
        r = (val - self.min_val) / (self.max_val - self.min_val)
        return self.track.x + int(r * self.track.w)

    def _xv(self, x):
        return self.min_val + clamp(
            (x - self.track.x) / self.track.w, 0, 1
        ) * (self.max_val - self.min_val)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            hx  = self._vx(self._value)
            hit = (math.hypot(event.pos[0] - hx,
                              event.pos[1] - self.track.centery) <= self.HANDLE_R + 6
                   or self.track.inflate(0, 26).collidepoint(event.pos))
            if hit:
                self.dragging = True
                self._value   = self._xv(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._value = self._xv(event.pos[0])
            return True
        return False

    def draw(self, surface):
        hx = self._vx(self._value)
        f  = self.fonts
        r  = self.HANDLE_R
        tr = theme.SLIDER_TRACK_R

        em  = f["label"].render(f"{self.emoji}  {self.label}", True, theme.TEXT)
        val = f["value"].render(str(self.value), True, self.color)
        surface.blit(em,  (self.track.x, self.track.y - 18))
        surface.blit(val, (self.track.right - val.get_width(), self.track.y - 19))

        track_rect = pygame.Rect(self.track.x, self.track.centery - self.TRACK_H // 2,
                                 self.track.w, self.TRACK_H)
        pygame.draw.rect(surface, theme.CARD_EDGE, track_rect, border_radius=tr)
        fw = hx - self.track.x
        if fw > 0:
            pygame.draw.rect(surface, self.color,
                             pygame.Rect(track_rect.x, track_rect.y, fw, track_rect.h),
                             border_radius=tr)

        glow = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, theme.SLIDER_GLOW_A), (r * 2, r * 2), r * 2)
        surface.blit(glow, (hx - r * 2, self.track.centery - r * 2))
        pygame.draw.circle(surface, self.color,      (hx, self.track.centery), r)
        pygame.draw.circle(surface, (255, 255, 255), (hx, self.track.centery),
                           r - theme.SLIDER_INNER_TRIM)
        pygame.draw.circle(surface, self.color,      (hx, self.track.centery),
                           r - theme.SLIDER_CORE_TRIM)
