"""CanvasWidget — displays the PIL drawing canvas via textual-image (TGP)."""
from textual.widget import Widget
from textual.app import ComposeResult
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
    """Wraps a TGPImage widget, auto-scales the PIL canvas to fill the area."""

    DEFAULT_CSS = """
    CanvasWidget {
        width: 1fr;
        layout: vertical;
        align: center middle;
        background: #06050f;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._last_pil: PILImage.Image | None = None

    def compose(self) -> ComposeResult:
        if _HAS_TEXTUAL_IMAGE:
            self._img = TImage(id="canvas-img")
            yield self._img
        else:
            from textual.widgets import Static
            yield Static(
                "[red]textual-image not installed.[/red]\n"
                "Run: pip install textual-image",
                id="canvas-img",
            )

    # ── Sizing helpers ────────────────────────────────────────────────────────

    def _target_px(self) -> int:
        """Largest square pixel size that fits in the current widget cell area."""
        w_cells = self.size.width  or 80
        h_cells = self.size.height or 40
        cell    = _get_cell_size()
        # Use the smaller of the two dimensions so the image fits without clipping
        return max(64, min(w_cells * cell.width, h_cells * cell.height) - 8)

    def _scaled(self, pil_image: PILImage.Image) -> PILImage.Image:
        px  = self._target_px()
        img = pil_image.copy()
        img.thumbnail((px, px), PILImage.LANCZOS)
        return img

    # ── Public API ────────────────────────────────────────────────────────────

    def refresh_canvas(self, pil_image: PILImage.Image) -> None:
        """Scale PIL image to fill the available area and push to TGPImage."""
        if not (_HAS_TEXTUAL_IMAGE and hasattr(self, "_img")):
            return
        self._last_pil = pil_image
        self._img.image = self._scaled(pil_image)

    # ── Resize event ─────────────────────────────────────────────────────────

    def on_resize(self, _event: events.Resize) -> None:
        """Re-render at new size when the terminal window changes."""
        if self._last_pil is not None and hasattr(self, "_img"):
            self._img.image = self._scaled(self._last_pil)
