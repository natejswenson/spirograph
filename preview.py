import math
import pygame
import theme
from spiro_math import SpiroMath
from utils import lerp_color
from constants import PREVIEW_SIZE


class PreviewWidget:
    """Animated toy-mechanism: outer ring, rolling inner wheel, pen arm,
    pen dot, ghost trace. Everything draws into a local surface so
    coordinates never leak into the parent panel's space."""

    def __init__(self, x, y, size):
        self.x    = x
        self.y    = y
        self.size = size
        self._angle        = 0.0
        self._ghost_pts    = []
        self._ghost_params = None
        self._spiro        = SpiroMath()

    def update(self, drawing):
        speed = theme.PREVIEW_SPIN_DRAW if drawing else theme.PREVIEW_SPIN_IDLE
        self._angle += speed

    def _get_ghost(self, R, r, d):
        params = (R, r, d)
        if params == self._ghost_params:
            return self._ghost_pts
        self._ghost_params = params
        raw     = self._spiro.compute_points(R, r, d, steps=theme.PREVIEW_GHOST_STEPS)
        max_ext = max(max(abs(px) for px, _ in raw),
                      max(abs(py) for _, py in raw), 1)
        scale   = (self.size * 0.5 - theme.PREVIEW_MARGIN) / max_ext
        half    = self.size // 2
        self._ghost_pts = [(half + px * scale, half + py * scale) for px, py in raw]
        return self._ghost_pts

    def draw(self, surface, R, r, d, pen_color, fonts):
        sz        = self.size
        local     = pygame.Surface((sz, sz), pygame.SRCALPHA)
        cx = cy   = sz // 2
        scale     = (sz // 2 - theme.PREVIEW_MARGIN) / (R + 4)
        r_clamped = min(r, R - 1)
        inner_rot = -(R - r_clamped) / max(r_clamped, 0.001) * self._angle

        # Ghost trace
        ghost = self._get_ghost(R, r, d)
        if len(ghost) > 1:
            pygame.draw.lines(local, (*pen_color[:3], theme.PREVIEW_GHOST_A),
                              False, [(int(px), int(py)) for px, py in ghost], 1)

        # Outer ring + tick marks
        R_px = int(R * scale)
        pygame.draw.circle(local, theme.PREVIEW_OUTER_RING, (cx, cy), R_px, 2)
        for i in range(12):
            a = i * math.pi / 6
            pygame.draw.line(local, theme.PREVIEW_TICK,
                             (cx + int((R_px - 5) * math.cos(a)),
                              cy + int((R_px - 5) * math.sin(a))),
                             (cx + int(R_px * math.cos(a)),
                              cy + int(R_px * math.sin(a))), 1)

        # Inner wheel
        wx   = cx + int((R - r_clamped) * scale * math.cos(self._angle))
        wy   = cy + int((R - r_clamped) * scale * math.sin(self._angle))
        r_px = max(2, int(r_clamped * scale))

        wf = pygame.Surface((r_px * 2 + 2, r_px * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(wf, (*theme.PREVIEW_WHEEL_FILL, theme.PREVIEW_WHEEL_FILL_A),
                           (r_px + 1, r_px + 1), r_px)
        local.blit(wf, (wx - r_px - 1, wy - r_px - 1))
        pygame.draw.circle(local, theme.SLIDER_COLORS[1], (wx, wy), r_px, 2)

        # Gear dots + crosshair
        n_teeth = max(4, int(r_clamped / 12))
        for i in range(n_teeth):
            ga = inner_rot + i * (2 * math.pi / n_teeth)
            pygame.draw.circle(local, theme.SLIDER_COLORS[1],
                               (wx + int((r_px - 3) * math.cos(ga)),
                                wy + int((r_px - 3) * math.sin(ga))), 2)
        pygame.draw.line(local, theme.PREVIEW_CROSSHAIR,
                         (wx - r_px + 4, wy), (wx + r_px - 4, wy), 1)
        pygame.draw.line(local, theme.PREVIEW_CROSSHAIR,
                         (wx, wy - r_px + 4), (wx, wy + r_px - 4), 1)

        # Pen arm + dot
        px2 = wx + int(d * scale * math.cos(inner_rot))
        py2 = wy + int(d * scale * math.sin(inner_rot))
        pygame.draw.line(local, (*theme.SLIDER_COLORS[2], theme.PREVIEW_PEN_ARM_A),
                         (wx, wy), (px2, py2), 2)
        pygame.draw.circle(local, pen_color,         (px2, py2), theme.PREVIEW_PEN_R)
        pygame.draw.circle(local, (255, 255, 255),   (px2, py2), theme.PREVIEW_PEN_RING_R)
        pygame.draw.circle(local, pen_color,         (px2, py2), theme.PREVIEW_PEN_CORE_R)

        # R= / r= labels
        f     = fonts["small"]
        lbl_R = f.render(f"R={R}", True,
                         lerp_color(theme.SLIDER_COLORS[0], (200, 200, 255),
                                    theme.PREVIEW_LABEL_LERP))
        local.blit(lbl_R, (cx - lbl_R.get_width() // 2, sz - 16))
        lbl_r = f.render(f"r={r}", True, theme.SLIDER_COLORS[1])
        local.blit(lbl_r, (min(wx + r_px + 3, sz - lbl_r.get_width() - 2), wy - 7))

        surface.blit(local, (self.x, self.y))
