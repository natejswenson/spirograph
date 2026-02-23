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

# ── Section-rule helper ───────────────────────────────────────────────────────

def _rule(label: str) -> Static:
    """Decorated horizontal rule: ─ LABEL ────────────────────"""
    text = f"─ {label} " + "─" * 50
    return Static(text, classes="section-rule")


class SpirographTUIApp(App):
    """Spirograph Studio — terminal edition."""

    CSS_PATH = os.path.join(os.path.dirname(__file__), "theme.tcss")

    BINDINGS = [
        Binding("ctrl+z", "undo",   "Undo"),
        Binding("escape", "quit",   "Quit"),
        Binding("q",      "quit",   "Quit", show=False),
        Binding("d",      "draw",   "Draw", show=False),
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
        with Horizontal(id="main"):
            with Vertical(id="panel"):
                yield Static("SPIROGRAPH STUDIO", id="panel-title")

                # Primary action
                yield Button("DRAW", id="btn-draw")

                # Secondary actions
                with Horizontal(id="btn-secondary"):
                    yield Button("UNDO",  id="btn-undo")
                    yield Button("CLEAR", id="btn-clear")
                    yield Button("SAVE",  id="btn-save")

                # Shape parameters
                yield _rule("SHAPE")
                yield SpiroSlider(
                    label="Big Circle",
                    mn=20, mx=200, init=150,
                    color=_theme.SLIDER_COLORS[0],
                    slider_id="slider-R",
                )
                yield SpiroSlider(
                    label="Little Wheel",
                    mn=10, mx=150, init=80,
                    color=_theme.SLIDER_COLORS[1],
                    slider_id="slider-r",
                )
                yield SpiroSlider(
                    label="Pen Reach",
                    mn=10, mx=150, init=100,
                    color=_theme.SLIDER_COLORS[2],
                    slider_id="slider-d",
                )

                # Render parameters
                yield _rule("RENDER")
                yield SpiroSlider(
                    label="Speed",
                    mn=1, mx=20, init=5,
                    color=_theme.SLIDER_COLORS[3],
                    slider_id="slider-speed",
                )
                yield SpiroSlider(
                    label="Thickness",
                    mn=1, mx=8, init=2,
                    color=_theme.SLIDER_COLORS[4],
                    slider_id="slider-thick",
                )

                # Color
                yield _rule("COLOR")
                yield ColorPicker(id="color-picker")

            yield CanvasWidget(id="canvas")

        yield Static("", id="footer")

    def on_mount(self) -> None:
        self.query_one(CanvasWidget).refresh_canvas(self._engine.canvas)
        self.set_interval(1 / 15, self._on_tick)

    # ── Tick ──────────────────────────────────────────────────────────────────

    async def _on_tick(self) -> None:
        cp = self._color_picker()
        self._engine.step(self._speed() * 5, self._thick(), cp)

        if self._engine.take_dirty():
            self.query_one(CanvasWidget).refresh_canvas(self._engine.canvas)

        # Draw button label — shows progress during animation
        btn = self.query_one("#btn-draw", Button)
        if self._engine.drawing:
            pct = int(100 * self._engine.draw_index / max(1, self._engine.draw_total))
            btn.label = f"DRAWING  {pct}%"
            btn.add_class("drawing")
        else:
            btn.label = "DRAW"
            btn.remove_class("drawing")

        # Footer status
        if self._save_flash > 0:
            self._save_flash -= 1
            self._update_footer(
                f"Saved  ·  R={self._R()}  r={self._r()}  d={self._d()}"
                f"  ·  layers={self._engine.layer_count}"
            )
        elif self._engine.drawing:
            pct = int(100 * self._engine.draw_index / max(1, self._engine.draw_total))
            self._update_footer(
                f"R={self._R()}  r={self._r()}  d={self._d()}"
                f"  ·  Drawing {pct}%"
                f"  ·  layers={self._engine.layer_count}"
            )
        else:
            self._update_footer(
                f"R={self._R()}  r={self._r()}  d={self._d()}"
                f"  ·  layers={self._engine.layer_count}"
                f"  ·  undo={self._engine.undo_count}"
            )

    def _update_footer(self, msg: str) -> None:
        self.query_one("#footer", Static).update(msg)

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

    def action_draw(self) -> None:
        self._engine.start(self._R(), self._r(), self._d())

    # ── Save ──────────────────────────────────────────────────────────────────

    def _save(self) -> None:
        fname = os.path.join(
            SAVE_DIR,
            f"spirograph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
        )
        self._engine.canvas.save(fname)
        self._save_flash = 45
