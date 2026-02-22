import pygame
from utils import lerp_color
from constants import C_CARD_EDGE


class Button:
    def __init__(self, x, y, w, h, icon, text, color, fonts):
        self.rect  = pygame.Rect(x, y, w, h)
        self.icon  = icon
        self.text  = text
        self.color = color
        self.fonts = fonts
        self._t    = 0.0   # hover lerp state

    def draw(self, surface, hovered):
        self._t += ((1.0 if hovered else 0.0) - self._t) * 0.2
        col = lerp_color(self.color,
                         tuple(min(255, c + 55) for c in self.color),
                         self._t)

        # Drop shadow
        sh = pygame.Surface((self.rect.w + 4, self.rect.h + 6), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 65), sh.get_rect(), border_radius=12)
        surface.blit(sh, (self.rect.x - 1, self.rect.y + 4))

        pygame.draw.rect(surface, col, self.rect, border_radius=10)

        # Gloss highlight on top half
        gl = pygame.Surface((self.rect.w - 4, self.rect.h // 2 - 2), pygame.SRCALPHA)
        gl.fill((255, 255, 255, 22))
        surface.blit(gl, (self.rect.x + 2, self.rect.y + 2))

        pygame.draw.rect(surface, C_CARD_EDGE, self.rect, 1, border_radius=10)

        lbl = self.fonts["btn"].render(f"{self.icon}  {self.text}", True, (255, 255, 255))
        surface.blit(lbl, lbl.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))
