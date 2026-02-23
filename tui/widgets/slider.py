"""SpiroSlider — two-line draggable slider widget for the TUI."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from textual.widget import Widget
from textual.reactive import reactive
from textual.binding import Binding
from textual.message import Message
from textual import events
from rich.text import Text

import theme


class SpiroSlider(Widget):
    """
    Two-line slider:
      Line 0 — LABEL (left)   VALUE (right, accent color)
      Line 1 — ██████▌──────  (full-width track + draggable handle)

    Interaction:
      Mouse  — click or drag anywhere on the track row
      Keys   — ← / → (±1),  Shift+← / Shift+→ (±10)
    """

    BINDINGS = [
        Binding("left",        "dec_small", "−1",  show=False),
        Binding("right",       "inc_small", "+1",  show=False),
        Binding("shift+left",  "dec_large", "−10", show=False),
        Binding("shift+right", "inc_large", "+10", show=False),
    ]

    value: reactive[int] = reactive(0, layout=True)

    # ── Inner message ─────────────────────────────────────────────────────────

    class ValueChanged(Message):
        def __init__(self, slider: "SpiroSlider", value: int) -> None:
            super().__init__()
            self.slider = slider
            self.value  = value

    # ── Construction ──────────────────────────────────────────────────────────

    def __init__(
        self,
        label: str,
        mn: int,
        mx: int,
        init: int,
        color: tuple,
        slider_id: str = "",
    ) -> None:
        super().__init__(id=slider_id or None)
        self.label     = label
        self.min_val   = mn
        self.max_val   = mx
        self._color    = color
        self.value     = init
        self.can_focus = True
        self._dragging = False

    # ── Rendering ─────────────────────────────────────────────────────────────

    def render(self) -> Text:
        r, g, b = self._color
        hx      = f"#{r:02x}{g:02x}{b:02x}"
        w       = max(12, self.size.width)
        val_str = str(self.value)

        # Line 0: label (left) + padding + value (right)
        text = Text(no_wrap=True)
        text.append(f" {self.label}", style="bold white")
        pad = w - 1 - len(self.label) - len(val_str) - 1
        text.append(" " * max(1, pad))
        text.append(val_str, style=f"bold {hx}")
        text.append("\n")

        # Line 1: track — filled ██ + white ▌ handle + empty ──
        track_w = max(4, w - 2)
        ratio   = (self.value - self.min_val) / max(1, self.max_val - self.min_val)
        filled  = max(0, min(track_w - 1, int(ratio * (track_w - 1))))
        empty   = track_w - filled - 1

        text.append(" ")
        text.append("█" * filled, style=hx)
        text.append("▌", style="bold white")
        text.append("─" * empty,  style="color(238)")
        text.append(" ")

        return text

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _set_value(self, v: int) -> None:
        clamped = max(self.min_val, min(self.max_val, v))
        if clamped != self.value:
            self.value = clamped
            self.post_message(self.ValueChanged(self, clamped))

    def _x_to_value(self, x: int) -> int:
        """Convert an x cell-coordinate to a slider value."""
        w       = self.size.width or 42
        track_w = max(4, w - 2)
        rel_x   = x - 1                     # 1-char left margin
        ratio   = max(0.0, min(1.0, rel_x / max(1, track_w - 1)))
        return int(self.min_val + ratio * (self.max_val - self.min_val))

    # ── Key actions ───────────────────────────────────────────────────────────

    def action_dec_small(self) -> None: self._set_value(self.value - 1)
    def action_inc_small(self) -> None: self._set_value(self.value + 1)
    def action_dec_large(self) -> None: self._set_value(self.value - 10)
    def action_inc_large(self) -> None: self._set_value(self.value + 10)

    # ── Mouse — click + drag ──────────────────────────────────────────────────

    def on_mouse_down(self, event: events.MouseDown) -> None:
        self.focus()
        self._dragging = True
        self.capture_mouse()                 # receive move/up events globally
        self._set_value(self._x_to_value(event.x))

    def on_mouse_move(self, event: events.MouseMove) -> None:
        if self._dragging:
            self._set_value(self._x_to_value(event.x))

    def on_mouse_up(self, event: events.MouseUp) -> None:
        if self._dragging:
            self._dragging = False
            self.release_mouse()
