import math
import pygame
from utils import clamp
from constants import C_CARD_EDGE, C_TEXT


class Slider:
    TRACK_H  = 7
    HANDLE_R = 11
    ROW_H    = 44

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
            hx = self._vx(self._value)
            hit = (math.hypot(event.pos[0] - hx,
                              event.pos[1] - self.track.centery) <= self.HANDLE_R + 6
                   or self.track.inflate(0, 26).collidepoint(event.pos))
            if hit:
                self.dragging = True
                self._value = self._xv(event.pos[0])
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

        em  = f["label"].render(f"{self.emoji}  {self.label}", True, C_TEXT)
        val = f["value"].render(str(self.value), True, self.color)
        surface.blit(em,  (self.track.x, self.track.y - 18))
        surface.blit(val, (self.track.right - val.get_width(), self.track.y - 19))

        tr = pygame.Rect(self.track.x, self.track.centery - self.TRACK_H // 2,
                         self.track.w, self.TRACK_H)
        pygame.draw.rect(surface, C_CARD_EDGE, tr, border_radius=4)
        fw = hx - self.track.x
        if fw > 0:
            pygame.draw.rect(surface, self.color,
                             pygame.Rect(tr.x, tr.y, fw, tr.h), border_radius=4)

        r = self.HANDLE_R
        glow = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 60), (r * 2, r * 2), r * 2)
        surface.blit(glow, (hx - r * 2, self.track.centery - r * 2))
        pygame.draw.circle(surface, self.color,         (hx, self.track.centery), r)
        pygame.draw.circle(surface, (255, 255, 255),    (hx, self.track.centery), r - 3)
        pygame.draw.circle(surface, self.color,         (hx, self.track.centery), r - 6)
