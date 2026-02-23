"""SpirographTUIApp — Textual TUI for Spirograph Studio."""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal
from textual.widgets import Button, Static

from constants import SAVE_DIR
import theme as _theme

from .drawing_engine import DrawingEngine
from .widgets.slider import SpiroSlider
from .widgets.color_picker import ColorPicker
from .widgets.canvas import CanvasWidget
from .widgets.preview import PreviewWidget

# ── Slider definitions (label, min, max, init, color_index, id) ──────────────
_SLIDERS = [
    ("Big Circle",   20, 200, 150, 0, "slider-R"),
    ("Little Wheel", 10, 150,  80, 1, "slider-r"),
    ("Pen Reach",    10, 150, 100, 2, "slider-d"),
    ("Speed",         1,  20,   5, 3, "slider-speed"),
    ("Thickness",     1,   8,   2, 4, "slider-thick"),
]


class SpirographTUIApp(App):
    """Spirograph Studio — terminal edition."""

    CSS_PATH = os.path.join(os.path.dirname(__file__), "theme.tcss")

    BINDINGS = [
        Binding("ctrl+z", "undo", "Undo"),
        Binding("escape", "quit", "Quit"),
        Binding("q",      "quit", "Quit", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._engine     = DrawingEngine()
        self._save_flash = 0

    # ── Convenience accessors ─────────────────────────────────────────────────

    def _R(self) -> int:
        return self.query_one("#slider-R", SpiroSlider).value

    def _r(self) -> int:
        return min(self.query_one("#slider-r", SpiroSlider).value, self._R() - 1)

    def _d(self) -> int:
        return self.query_one("#slider-d", SpiroSlider).value

    def _speed(self) -> int:
        return self.query_one("#slider-speed", SpiroSlider).value

    def _thick(self) -> int:
        return self.query_one("#slider-thick", SpiroSlider).value

    def _color_picker(self) -> ColorPicker:
        return self.query_one(ColorPicker)

    def _pen_color(self) -> tuple:
        return self._color_picker().current_solid()

    # ── Layout ────────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        with Vertical(id="panel"):
            yield Static("SPIROGRAPH STUDIO", id="panel-title")
            yield PreviewWidget(id="preview")

            yield Static("PARAMETERS", classes="section-header")
            for label, mn, mx, init, color_idx, sid in _SLIDERS:
                yield SpiroSlider(
                    label=label,
                    mn=mn,
                    mx=mx,
                    init=init,
                    color=_theme.SLIDER_COLORS[color_idx],
                    slider_id=sid,
                )

            yield Static("COLOR", classes="section-header")
            yield ColorPicker(id="color-picker")

            yield Static("ACTIONS", classes="section-header")
            with Horizontal(id="btn-row-1"):
                yield Button("DRAW",  id="btn-draw",  variant="primary")
                yield Button("UNDO",  id="btn-undo",  variant="warning")
            with Horizontal(id="btn-row-2"):
                yield Button("CLEAR", id="btn-clear", variant="error")
                yield Button("SAVE",  id="btn-save",  variant="success")

            yield Static("", id="status")

        yield CanvasWidget(id="canvas")

    def on_mount(self) -> None:
        self.query_one(CanvasWidget).refresh_canvas(self._engine.canvas)
        self.set_interval(1 / 15, self._on_tick)

    # ── Tick ──────────────────────────────────────────────────────────────────

    async def _on_tick(self) -> None:
        cp = self._color_picker()
        self._engine.step(self._speed() * 5, self._thick(), cp)

        self.query_one(PreviewWidget).update(
            self._R(), self._r(), self._d(),
            self._pen_color(),
            self._engine.drawing,
        )

        if self._engine.take_dirty():
            self.query_one(CanvasWidget).refresh_canvas(self._engine.canvas)

        # Status bar
        if self._save_flash > 0:
            self._save_flash -= 1
            self._update_status(f"Saved  ·  layers={self._engine.layer_count}")
        elif self._engine.drawing:
            pct = int(100 * self._engine.draw_index / max(1, self._engine.draw_total))
            self._update_status(f"Drawing  {pct}%  ·  undo={self._engine.undo_count}")
        else:
            self._update_status(
                f"layers={self._engine.layer_count}  ·  undo={self._engine.undo_count}"
            )

    def _update_status(self, msg: str) -> None:
        self.query_one("#status", Static).update(msg)

    # ── Button callbacks ──────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-draw":
            self._engine.start(self._R(), self._r(), self._d())
        elif bid == "btn-undo":
            self._engine.pop_undo()
            self.query_one(CanvasWidget).refresh_canvas(self._engine.canvas)
        elif bid == "btn-clear":
            self._engine.clear()
            self.query_one(CanvasWidget).refresh_canvas(self._engine.canvas)
        elif bid == "btn-save":
            self._save()

    # ── Key actions ───────────────────────────────────────────────────────────

    def action_undo(self) -> None:
        self._engine.pop_undo()
        self.query_one(CanvasWidget).refresh_canvas(self._engine.canvas)

    # ── Save ──────────────────────────────────────────────────────────────────

    def _save(self) -> None:
        fname = os.path.join(
            SAVE_DIR,
            f"spirograph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
        )
        self._engine.canvas.save(fname)
        self._save_flash = 45
