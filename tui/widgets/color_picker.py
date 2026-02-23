"""ColorPicker — swatch grid + rainbow toggle for the TUI."""
import colorsys
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from textual.widget import Widget
from textual.reactive import reactive
from textual.message import Message
from textual import events
from textual.binding import Binding
from rich.text import Text

import theme


class ColorPicker(Widget):
    """Eight color swatches plus a rainbow mode toggle."""

    BINDINGS = [
        Binding("left",  "prev_swatch", "←", show=False),
        Binding("right", "next_swatch", "→", show=False),
        Binding("r",     "toggle_rainbow", "rainbow", show=False),
    ]

    selected: reactive[int]  = reactive(0, layout=True)
    rainbow:  reactive[bool] = reactive(False, layout=True)

    # ── Inner message ─────────────────────────────────────────────────────────

    class ColorChanged(Message):
        def __init__(self, picker: "ColorPicker", selected: int, rainbow: bool) -> None:
            super().__init__()
            self.picker   = picker
            self.selected = selected
            self.rainbow  = rainbow

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.can_focus = True

    # ── Rendering ─────────────────────────────────────────────────────────────

    def render(self) -> Text:
        text = Text(no_wrap=True, overflow="ellipsis")
        text.append("🎨  Color\n", style="bold color(245)")

        for i, (r, g, b) in enumerate(theme.PRESET_COLORS):
            hex_col = f"#{r:02x}{g:02x}{b:02x}"
            if i == self.selected and not self.rainbow:
                text.append("▐█▌", style=f"bold {hex_col} on {hex_col}")
            else:
                text.append(" █ ", style=f"{hex_col} on {hex_col}")
        text.append("\n")

        # Rainbow toggle line
        if self.rainbow:
            rb_hex = "#{:02x}{:02x}{:02x}".format(*theme.RAINBOW_ACTIVE_COLOR)
            text.append("[✓] 🌈  Rainbow!", style=f"bold {rb_hex}")
        else:
            text.append("[ ] 🌈  Rainbow!",  style="color(240)")
        return text

    # ── Color access (same interface as Pygame ColorPicker) ───────────────────

    def get_color(self, idx: int, total: int) -> tuple:
        if self.rainbow:
            h = (idx / max(total, 1)) % 1.0
            r, g, b = colorsys.hsv_to_rgb(h, 1.0, 1.0)
            return (int(r * 255), int(g * 255), int(b * 255))
        return theme.PRESET_COLORS[self.selected]

    def current_solid(self) -> tuple:
        return theme.PRESET_COLORS[self.selected]

    # ── Actions ───────────────────────────────────────────────────────────────

    def action_prev_swatch(self) -> None:
        self.selected = (self.selected - 1) % len(theme.PRESET_COLORS)
        self.rainbow  = False
        self._emit()

    def action_next_swatch(self) -> None:
        self.selected = (self.selected + 1) % len(theme.PRESET_COLORS)
        self.rainbow  = False
        self._emit()

    def action_toggle_rainbow(self) -> None:
        self.rainbow = not self.rainbow
        self._emit()

    def _emit(self) -> None:
        self.post_message(self.ColorChanged(self, self.selected, self.rainbow))

    # ── Mouse ─────────────────────────────────────────────────────────────────

    def on_mouse_down(self, event: events.MouseDown) -> None:
        self.focus()
        # Row 0 is the label, row 1 is the swatches (3 chars each)
        if event.y == 1:
            # Each swatch is 3 chars wide
            swatch_idx = event.x // 3
            if 0 <= swatch_idx < len(theme.PRESET_COLORS):
                self.selected = swatch_idx
                self.rainbow  = False
                self._emit()
        elif event.y == 2:
            # Rainbow toggle row
            self.action_toggle_rainbow()
