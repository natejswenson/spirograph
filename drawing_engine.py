import pygame
from spiro_math import SpiroMath
from utils import make_canvas_bg
from constants import CANVAS_SIZE


class DrawingEngine:
    """Owns the canvas surface, undo stack, and drawing animation state."""

    MAX_UNDO = 20

    def __init__(self):
        self._spiro      = SpiroMath()
        self._canvas_bg  = make_canvas_bg(CANVAS_SIZE)
        self.canvas      = self._canvas_bg.copy()
        self.drawing     = False
        self.draw_index  = 0
        self.draw_points = []
        self.draw_total  = 0
        self.layer_count = 0
        self._undo_stack = []

    # ── Undo ───────────────────────────────────────────────────────────────────
    def push_undo(self):
        self._undo_stack.append(self.canvas.copy())
        if len(self._undo_stack) > self.MAX_UNDO:
            self._undo_stack.pop(0)

    def pop_undo(self):
        if self._undo_stack:
            self.drawing     = False
            self.canvas      = self._undo_stack.pop()
            self.layer_count = max(0, self.layer_count - 1)

    @property
    def undo_count(self):
        return len(self._undo_stack)

    # ── Canvas control ─────────────────────────────────────────────────────────
    def clear(self):
        self.push_undo()
        self.drawing     = False
        self.canvas      = self._canvas_bg.copy()
        self.layer_count = 0

    # ── Drawing ────────────────────────────────────────────────────────────────
    def start(self, R, r, d):
        pts     = self._spiro.compute_points(R, r, d)
        max_ext = max(max(abs(v) for pt in pts for v in pt), 1)
        scale   = (CANVAS_SIZE / 2 - 28) / max_ext
        cx = cy = CANVAS_SIZE // 2
        self.draw_points = [(cx + x * scale, cy + y * scale) for x, y in pts]
        self.draw_total  = len(self.draw_points)
        self.draw_index  = 1
        self.push_undo()
        self.drawing = True

    def step(self, speed, thick, color_picker):
        if not self.drawing:
            return
        for _ in range(speed):
            if self.draw_index >= self.draw_total:
                self.drawing      = False
                self.layer_count += 1
                break
            p1  = self.draw_points[self.draw_index - 1]
            p2  = self.draw_points[self.draw_index]
            col = color_picker.get_color(self.draw_index, self.draw_total)
            pygame.draw.line(self.canvas, col,
                             (int(p1[0]), int(p1[1])),
                             (int(p2[0]), int(p2[1])), thick)
            self.draw_index += 1
