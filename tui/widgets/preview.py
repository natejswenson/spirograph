"""PreviewWidget — animated PIL mechanism preview for the TUI."""
import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from textual.widget import Widget
from textual.app import ComposeResult

try:
    from textual_image.widget import TGPImage as TImage
    _HAS_TEXTUAL_IMAGE = True
except ImportError:
    _HAS_TEXTUAL_IMAGE = False

from PIL import Image as PILImage, ImageDraw

from spiro_math import SpiroMath
import theme
from constants import PREVIEW_SIZE


class PreviewWidget(Widget):
    """Animated mechanism preview: outer ring, rolling inner wheel, pen arm, ghost trace."""

    DEFAULT_CSS = """
    PreviewWidget {
        height: auto;
        align: center top;
        padding: 0;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._angle        = 0.0
        self._ghost_pts    = []
        self._ghost_params = None
        self._spiro        = SpiroMath()
        self._last_frame: PILImage.Image | None = None

    def compose(self) -> ComposeResult:
        if _HAS_TEXTUAL_IMAGE:
            self._img = TImage(id="preview-img")
            yield self._img
        else:
            from textual.widgets import Static
            yield Static("[dim]preview unavailable[/dim]", id="preview-img")

    # ── Ghost trace cache ─────────────────────────────────────────────────────

    def _get_ghost(self, R: float, r: float, d: float) -> list:
        params = (R, r, d)
        if params == self._ghost_params:
            return self._ghost_pts
        self._ghost_params = params
        raw     = self._spiro.compute_points(R, r, d, steps=theme.PREVIEW_GHOST_STEPS)
        max_ext = max(max(abs(v) for pt in raw for v in pt), 1)
        scale   = (PREVIEW_SIZE * 0.5 - theme.PREVIEW_MARGIN) / max_ext
        half    = PREVIEW_SIZE // 2
        self._ghost_pts = [(half + px * scale, half + py * scale) for px, py in raw]
        return self._ghost_pts

    # ── PIL frame renderer ────────────────────────────────────────────────────

    def _draw_frame(
        self,
        R: float,
        r: float,
        d: float,
        pen_color: tuple,
    ) -> PILImage.Image:
        sz        = PREVIEW_SIZE
        cx = cy   = sz // 2
        scale     = (sz // 2 - theme.PREVIEW_MARGIN) / (R + 4)
        r_clamped = min(r, R - 1)
        inner_rot = -(R - r_clamped) / max(r_clamped, 0.001) * self._angle

        img  = PILImage.new("RGBA", (sz, sz), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img, "RGBA")

        # Ghost trace
        ghost = self._get_ghost(R, r, d)
        if len(ghost) > 1:
            ga = theme.PREVIEW_GHOST_A
            pts_int = [(int(x), int(y)) for x, y in ghost]
            draw.line(pts_int, fill=(*pen_color[:3], ga), width=1)

        # Outer ring
        R_px = int(R * scale)
        draw.ellipse(
            [(cx - R_px, cy - R_px), (cx + R_px, cy + R_px)],
            outline=theme.PREVIEW_OUTER_RING,
            width=2,
        )

        # Tick marks
        for i in range(12):
            a   = i * math.pi / 6
            cos_a, sin_a = math.cos(a), math.sin(a)
            draw.line(
                [
                    (cx + int((R_px - 5) * cos_a), cy + int((R_px - 5) * sin_a)),
                    (cx + int(R_px * cos_a),        cy + int(R_px * sin_a)),
                ],
                fill=theme.PREVIEW_TICK,
                width=1,
            )

        # Inner wheel
        wheel_x = cx + int((R - r_clamped) * scale * math.cos(self._angle))
        wheel_y = cy + int((R - r_clamped) * scale * math.sin(self._angle))
        r_px    = max(2, int(r_clamped * scale))

        # Filled wheel (with alpha)
        wf = theme.PREVIEW_WHEEL_FILL
        draw.ellipse(
            [(wheel_x - r_px, wheel_y - r_px), (wheel_x + r_px, wheel_y + r_px)],
            fill=(*wf, theme.PREVIEW_WHEEL_FILL_A),
            outline=theme.SLIDER_COLORS[1],
            width=2,
        )

        # Gear dots
        n_teeth = max(4, int(r_clamped / 12))
        for i in range(n_teeth):
            ga = inner_rot + i * (2 * math.pi / n_teeth)
            dx = int((r_px - 3) * math.cos(ga))
            dy = int((r_px - 3) * math.sin(ga))
            draw.ellipse(
                [(wheel_x + dx - 2, wheel_y + dy - 2),
                 (wheel_x + dx + 2, wheel_y + dy + 2)],
                fill=theme.SLIDER_COLORS[1],
            )

        # Crosshair
        draw.line(
            [(wheel_x - r_px + 4, wheel_y), (wheel_x + r_px - 4, wheel_y)],
            fill=theme.PREVIEW_CROSSHAIR, width=1,
        )
        draw.line(
            [(wheel_x, wheel_y - r_px + 4), (wheel_x, wheel_y + r_px - 4)],
            fill=theme.PREVIEW_CROSSHAIR, width=1,
        )

        # Pen arm
        pen_x = wheel_x + int(d * scale * math.cos(inner_rot))
        pen_y = wheel_y + int(d * scale * math.sin(inner_rot))
        arm_a = theme.PREVIEW_PEN_ARM_A
        draw.line(
            [(wheel_x, wheel_y), (pen_x, pen_y)],
            fill=(*theme.SLIDER_COLORS[2], arm_a),
            width=2,
        )

        # Pen dot (outer, white ring, colored center)
        pr = theme.PREVIEW_PEN_R
        draw.ellipse(
            [(pen_x - pr, pen_y - pr), (pen_x + pr, pen_y + pr)],
            fill=pen_color,
        )
        ring_r = theme.PREVIEW_PEN_RING_R
        draw.ellipse(
            [(pen_x - ring_r, pen_y - ring_r), (pen_x + ring_r, pen_y + ring_r)],
            fill=(255, 255, 255),
        )
        core_r = theme.PREVIEW_PEN_CORE_R
        draw.ellipse(
            [(pen_x - core_r, pen_y - core_r), (pen_x + core_r, pen_y + core_r)],
            fill=pen_color,
        )

        # R= / r= labels (skip text — PIL font loading is complex in TUI context)
        # The labels are decorative; omit to avoid font dependency issues.

        # Flatten RGBA onto the canvas background color
        bg_r, bg_g, bg_b = theme.CANVAS_BG
        bg = PILImage.new("RGBA", (sz, sz), (bg_r, bg_g, bg_b, 255))
        bg.paste(img, mask=img)
        return bg.convert("RGB")

    # ── Public update call (called each tick from app) ────────────────────────

    def update(self, R: float, r: float, d: float, pen_color: tuple, drawing: bool) -> None:
        speed = theme.PREVIEW_SPIN_DRAW if drawing else theme.PREVIEW_SPIN_IDLE
        self._angle += speed
        frame = self._draw_frame(R, r, d, pen_color)
        self._last_frame = frame
        if _HAS_TEXTUAL_IMAGE and hasattr(self, "_img"):
            self._img.image = frame  # setter calls refresh(layout=True) internally
