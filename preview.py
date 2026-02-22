import math
import pygame
from spiro_math import SpiroMath
from utils import lerp_color
from constants import SLIDER_COLORS


class PreviewWidget:
    """Animated toy-mechanism preview: outer ring, rolling inner wheel,
    pen arm, pen dot, and a faint ghost trace of the full curve."""

    def __init__(self, x, y, size):
        self.x    = x
        self.y    = y
        self.size = size
        self._angle        = 0.0
        self._ghost_pts    = []
        self._ghost_params = None
        self._spiro        = SpiroMath()

    def update(self, drawing):
        self._angle += 0.055 if drawing else 0.018

    # ── Ghost curve cache ──────────────────────────────────────────────────────
    def _get_ghost(self, R, r, d):
        params = (R, r, d)
        if params == self._ghost_params:
            return self._ghost_pts
        self._ghost_params = params
        raw     = self._spiro.compute_points(R, r, d, steps=900)
        max_ext = max(max(abs(px) for px, _ in raw),
                      max(abs(py) for _, py in raw), 1)
        scale   = (self.size * 0.5 - 10) / max_ext
        half    = self.size // 2
        self._ghost_pts = [(half + px * scale, half + py * scale) for px, py in raw]
        return self._ghost_pts

    # ── Main draw (everything in local surface coords) ─────────────────────────
    def draw(self, surface, R, r, d, pen_color, fonts):
        sz    = self.size
        local = pygame.Surface((sz, sz), pygame.SRCALPHA)
        cx = cy = sz // 2
        scale   = (sz // 2 - 10) / (R + 4)
        r_clamped   = min(r, R - 1)
        inner_rot   = -(R - r_clamped) / max(r_clamped, 0.001) * self._angle

        # Ghost trace
        ghost = self._get_ghost(R, r, d)
        if len(ghost) > 1:
            pygame.draw.lines(local, (*pen_color[:3], 50), False,
                              [(int(px), int(py)) for px, py in ghost], 1)

        # Outer ring + tick marks
        R_px = int(R * scale)
        pygame.draw.circle(local, (65, 60, 110), (cx, cy), R_px, 2)
        for i in range(12):
            a = i * math.pi / 6
            pygame.draw.line(local, (85, 80, 135),
                             (cx + int((R_px - 5) * math.cos(a)),
                              cy + int((R_px - 5) * math.sin(a))),
                             (cx + int(R_px * math.cos(a)),
                              cy + int(R_px * math.sin(a))), 1)

        # Inner wheel
        wx   = cx + int((R - r_clamped) * scale * math.cos(self._angle))
        wy   = cy + int((R - r_clamped) * scale * math.sin(self._angle))
        r_px = max(2, int(r_clamped * scale))

        wf = pygame.Surface((r_px * 2 + 2, r_px * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(wf, (40, 38, 70, 180), (r_px + 1, r_px + 1), r_px)
        local.blit(wf, (wx - r_px - 1, wy - r_px - 1))
        pygame.draw.circle(local, SLIDER_COLORS[1], (wx, wy), r_px, 2)

        # Gear dots + crosshair
        for i in range(max(4, int(r_clamped / 12))):
            ga = inner_rot + i * (2 * math.pi / max(4, int(r_clamped / 12)))
            pygame.draw.circle(local, SLIDER_COLORS[1],
                               (wx + int((r_px - 3) * math.cos(ga)),
                                wy + int((r_px - 3) * math.sin(ga))), 2)
        pygame.draw.line(local, (70, 65, 110),
                         (wx - r_px + 4, wy), (wx + r_px - 4, wy), 1)
        pygame.draw.line(local, (70, 65, 110),
                         (wx, wy - r_px + 4), (wx, wy + r_px - 4), 1)

        # Pen arm + dot
        px2 = wx + int(d * scale * math.cos(inner_rot))
        py2 = wy + int(d * scale * math.sin(inner_rot))
        pygame.draw.line(local, (*SLIDER_COLORS[2], 200), (wx, wy), (px2, py2), 2)
        pygame.draw.circle(local, pen_color,       (px2, py2), 5)
        pygame.draw.circle(local, (255, 255, 255), (px2, py2), 3)
        pygame.draw.circle(local, pen_color,       (px2, py2), 2)

        # R= / r= labels
        f = fonts["small"]
        lbl_R = f.render(f"R={R}", True, lerp_color(SLIDER_COLORS[0], (200, 200, 255), 0.4))
        local.blit(lbl_R, (cx - lbl_R.get_width() // 2, sz - 16))
        lbl_r = f.render(f"r={r}", True, SLIDER_COLORS[1])
        local.blit(lbl_r, (min(wx + r_px + 3, sz - lbl_r.get_width() - 2), wy - 7))

        surface.blit(local, (self.x, self.y))
