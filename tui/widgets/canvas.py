"""CanvasWidget — displays the PIL drawing canvas via textual-image (TGP)."""
from textual.widget import Widget
from textual.app import ComposeResult
from textual.containers import Middle, Center
from textual import events

try:
    from textual_image.widget import TGPImage as TImage
    from textual_image._terminal import get_cell_size as _get_cell_size
    _HAS_TEXTUAL_IMAGE = True
except ImportError:
    _HAS_TEXTUAL_IMAGE = False
    def _get_cell_size():
        from types import SimpleNamespace
        return SimpleNamespace(width=10, height=20)

from PIL import Image as PILImage


class CanvasWidget(Widget):
    """Wraps TGPImage inside Middle+Center containers so it is always
    pixel-perfect centered in the canvas area regardless of terminal size."""

    DEFAULT_CSS = """
    CanvasWidget {
        width: 1fr;
        background: #06050f;
    }
    CanvasWidget Middle {
        width: 1fr;
        height: 1fr;
        background: #06050f;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._last_pil: PILImage.Image | None = None

    def compose(self) -> ComposeResult:
        if _HAS_TEXTUAL_IMAGE:
            self._img = TImage(id="canvas-img")
            with Middle():
                with Center():
                    yield self._img
        else:
            from textual.widgets import Static
            with Middle():
                yield Static(
                    "[red]textual-image not installed.[/red]\n"
                    "Run: pip install textual-image",
                    id="canvas-img",
                )

    # ── Sizing ────────────────────────────────────────────────────────────────

    def _target_px(self) -> int:
        """Largest square (px) that fits within the widget's current cell area."""
        w = self.size.width  or 80
        h = self.size.height or 40
        cell = _get_cell_size()
        return max(64, min(w * cell.width, h * cell.height) - 8)

    def _scaled(self, img: PILImage.Image) -> PILImage.Image:
        px  = self._target_px()
        out = img.copy()
        out.thumbnail((px, px), PILImage.LANCZOS)
        return out

    # ── Public API ────────────────────────────────────────────────────────────

    def refresh_canvas(self, pil_image: PILImage.Image) -> None:
        """Scale PIL image to fit available area and push to TGPImage."""
        if not (_HAS_TEXTUAL_IMAGE and hasattr(self, "_img")):
            return
        self._last_pil = pil_image
        self._img.image = self._scaled(pil_image)

    def on_resize(self, _event: events.Resize) -> None:
        if self._last_pil is not None and hasattr(self, "_img"):
            self._img.image = self._scaled(self._last_pil)
