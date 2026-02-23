"""SpiroSlider — keyboard + mouse slider widget for the TUI."""
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

# Fixed layout constants (panel content width is ~38 chars)
_LABEL_W = 13   # label padded to this width
_VAL_W   = 4    # max digit width (e.g. "200")


class SpiroSlider(Widget):
    """A horizontal slider rendered with Rich markup, driven by keyboard and mouse."""

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

    # ── Rendering ─────────────────────────────────────────────────────────────

    def render(self) -> Text:
        r, g, b = self._color
        hx      = f"#{r:02x}{g:02x}{b:02x}"

        w       = self.size.width or 38
        # layout:  LABEL(13) + " " + TRACK + "  " + VALUE(4)
        track_w = max(4, w - _LABEL_W - 1 - 2 - _VAL_W)
        ratio   = (self.value - self.min_val) / max(1, self.max_val - self.min_val)
        filled  = max(0, min(track_w, int(ratio * track_w)))
        empty   = track_w - filled

        text = Text(no_wrap=True, overflow="ellipsis")
        text.append(f"{self.label:<{_LABEL_W}}", style="bold white")
        text.append(" ")
        text.append("█" * filled, style=hx)
        text.append("─" * empty,  style="color(238)")
        text.append("  ")
        text.append(f"{self.value:>{_VAL_W}}", style=f"bold {hx}")
        return text

    # ── Value helpers ─────────────────────────────────────────────────────────

    def _set_value(self, v: int) -> None:
        clamped = max(self.min_val, min(self.max_val, v))
        if clamped != self.value:
            self.value = clamped
            self.post_message(self.ValueChanged(self, clamped))

    # ── Key actions ───────────────────────────────────────────────────────────

    def action_dec_small(self) -> None: self._set_value(self.value - 1)
    def action_inc_small(self) -> None: self._set_value(self.value + 1)
    def action_dec_large(self) -> None: self._set_value(self.value - 10)
    def action_inc_large(self) -> None: self._set_value(self.value + 10)

    # ── Mouse ─────────────────────────────────────────────────────────────────

    def on_mouse_down(self, event: events.MouseDown) -> None:
        self.focus()
        w         = self.size.width or 38
        track_w   = max(4, w - _LABEL_W - 1 - 2 - _VAL_W)
        track_x0  = _LABEL_W + 1   # where track begins
        rel_x     = event.x - track_x0
        ratio     = max(0.0, min(1.0, rel_x / max(1, track_w)))
        self._set_value(int(self.min_val + ratio * (self.max_val - self.min_val)))
