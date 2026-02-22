import pygame
import theme
from utils import lerp_color


class Button:
    def __init__(self, x, y, w, h, icon, text, color, fonts):
        self.rect  = pygame.Rect(x, y, w, h)
        self.icon  = icon
        self.text  = text
        self.color = color
        self.fonts = fonts
        self._t    = 0.0

    def draw(self, surface, hovered):
        self._t += ((1.0 if hovered else 0.0) - self._t) * theme.BTN_HOVER_LERP
        col = lerp_color(self.color,
                         tuple(min(255, c + theme.BTN_HOVER_BOOST) for c in self.color),
                         self._t)

        sh = pygame.Surface((self.rect.w + 4, self.rect.h + 6), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, theme.BTN_SHADOW_A),
                         sh.get_rect(), border_radius=theme.BTN_SHADOW_R)
        surface.blit(sh, (self.rect.x - 1, self.rect.y + 4))

        pygame.draw.rect(surface, col, self.rect, border_radius=theme.BTN_RADIUS)

        gloss = pygame.Surface((self.rect.w - 4, self.rect.h // 2 - 2), pygame.SRCALPHA)
        gloss.fill((255, 255, 255, theme.BTN_GLOSS_A))
        surface.blit(gloss, (self.rect.x + 2, self.rect.y + 2))

        pygame.draw.rect(surface, theme.CARD_EDGE, self.rect,
                         theme.BTN_BORDER_W, border_radius=theme.BTN_RADIUS)

        lbl = self.fonts["btn"].render(f"{self.icon}  {self.text}", True, (255, 255, 255))
        surface.blit(lbl, lbl.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))
