"""PIL-based DrawingEngine — mirrors drawing_engine.py with PIL backend."""
import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PIL import Image, ImageDraw

from spiro_math import SpiroMath
import theme
from constants import CANVAS_SIZE, CANVAS_MARGIN


def _make_canvas_bg(size: int) -> Image.Image:
    """Create the dot-grid background (same logic as utils.make_canvas_bg)."""
    r, g, b = theme.CANVAS_BG
    img = Image.new("RGB", (size, size), (r, g, b))
    sp   = theme.GRID_SPACING
    base = theme.GRID_BASE_BRIGHT
    amp  = theme.GRID_VARY_AMP
    freq = theme.GRID_VARY_FREQ
    tint = theme.GRID_BLUE_TINT
    for gx in range(sp, size, sp):
        for gy in range(sp, size, sp):
            c = base + int(amp * math.sin(gx * freq) * math.cos(gy * freq))
            img.putpixel((gx, gy), (c, c, c + tint))
    return img


class DrawingEngine:
    """Owns the PIL canvas, undo stack, and drawing animation state."""

    MAX_UNDO = 20

    def __init__(self):
        self._spiro      = SpiroMath()
        self._canvas_bg  = _make_canvas_bg(CANVAS_SIZE)
        self.canvas      = self._canvas_bg.copy()
        self.drawing     = False
        self.draw_index  = 0
        self.draw_points = []
        self.draw_total  = 0
        self.layer_count = 0
        self._undo_stack = []
        self._dirty      = True  # start dirty so initial canvas is sent

    # ── Undo ──────────────────────────────────────────────────────────────────

    def push_undo(self):
        self._undo_stack.append(self.canvas.copy())
        if len(self._undo_stack) > self.MAX_UNDO:
            self._undo_stack.pop(0)

    def pop_undo(self):
        if self._undo_stack:
            self.drawing     = False
            self.canvas      = self._undo_stack.pop()
            self.layer_count = max(0, self.layer_count - 1)
            self._dirty      = True

    @property
    def undo_count(self):
        return len(self._undo_stack)

    # ── Canvas control ────────────────────────────────────────────────────────

    def clear(self):
        self.push_undo()
        self.drawing     = False
        self.canvas      = self._canvas_bg.copy()
        self.layer_count = 0
        self._dirty      = True

    # ── Drawing ───────────────────────────────────────────────────────────────

    def start(self, R, r, d):
        pts     = self._spiro.compute_points(R, r, d)
        max_ext = max(max(abs(v) for pt in pts for v in pt), 1)
        scale   = (CANVAS_SIZE / 2 - CANVAS_MARGIN) / max_ext
        cx = cy = CANVAS_SIZE // 2
        self.draw_points = [(cx + x * scale, cy + y * scale) for x, y in pts]
        self.draw_total  = len(self.draw_points)
        self.draw_index  = 1
        self.push_undo()
        self.drawing = True
        self._dirty  = False

    def step(self, speed: int, thick: int, color_picker) -> None:
        if not self.drawing:
            return
        draw     = ImageDraw.Draw(self.canvas)
        advanced = False
        for _ in range(speed):
            if self.draw_index >= self.draw_total:
                self.drawing      = False
                self.layer_count += 1
                self._dirty       = True
                break
            p1  = self.draw_points[self.draw_index - 1]
            p2  = self.draw_points[self.draw_index]
            col = color_picker.get_color(self.draw_index, self.draw_total)
            draw.line(
                [(int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1]))],
                fill=col,
                width=max(1, thick),
            )
            self.draw_index += 1
            advanced = True
        if advanced:
            self._dirty = True

    def take_dirty(self) -> bool:
        """Return True if canvas was updated since last call; resets the flag."""
        d = self._dirty
        self._dirty = False
        return d
