"""SpiroSlider — keyboard + mouse slider widget for the TUI."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from textual.widget import Widget
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.binding import Binding
from textual.message import Message
from textual import events
from rich.text import Text

import theme


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
        emoji: str,
        label: str,
        mn: int,
        mx: int,
        init: int,
        color: tuple,
        slider_id: str = "",
    ) -> None:
        super().__init__(id=slider_id or None)
        self.emoji     = emoji
        self.label     = label
        self.min_val   = mn
        self.max_val   = mx
        self._color    = color
        self.value     = init
        self.can_focus = True

    # ── Rendering ─────────────────────────────────────────────────────────────

    def render(self) -> Text:
        r, g, b   = self._color
        hex_color = f"#{r:02x}{g:02x}{b:02x}"

        # Track dimensions — use widget width minus label/value space
        width      = self.size.width
        label_len  = len(f"{self.emoji}  {self.label}  ") + len(str(self.max_val))
        track_w    = max(8, width - label_len - 2)
        ratio      = (self.value - self.min_val) / max(1, self.max_val - self.min_val)
        filled     = max(0, min(track_w, int(ratio * track_w)))
        empty      = track_w - filled

        text = Text(no_wrap=True, overflow="ellipsis")
        text.append(f"{self.emoji}  {self.label}  ", style="bold white")
        text.append("█" * filled,  style=f"bold {hex_color}")
        text.append("░" * empty,   style="color(240)")
        text.append(f"  {self.value:>4}", style=f"bold {hex_color}")
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
        width     = self.size.width
        label_len = len(f"{self.emoji}  {self.label}  ") + len(str(self.max_val))
        # track starts after the label portion (approx)
        track_start = len(f"{self.emoji}  {self.label}  ")
        track_w     = max(8, width - label_len - 2)
        rel_x       = event.x - track_start
        ratio       = max(0.0, min(1.0, rel_x / max(1, track_w)))
        new_val     = int(self.min_val + ratio * (self.max_val - self.min_val))
        self._set_value(new_val)
