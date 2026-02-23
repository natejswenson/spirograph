"""CanvasWidget — displays the PIL drawing canvas via textual-image (TGP)."""
from textual.widget import Widget
from textual.app import ComposeResult

try:
    from textual_image.widget import TGPImage as TImage
    _HAS_TEXTUAL_IMAGE = True
except ImportError:
    _HAS_TEXTUAL_IMAGE = False

from PIL import Image as PILImage


class CanvasWidget(Widget):
    """Wraps a textual_image Image widget and exposes refresh_canvas()."""

    DEFAULT_CSS = """
    CanvasWidget {
        width: 1fr;
        align: center middle;
        padding: 1;
    }
    """

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

    def refresh_canvas(self, pil_image: PILImage.Image) -> None:
        """Push a new PIL image to the display widget."""
        if _HAS_TEXTUAL_IMAGE and hasattr(self, "_img"):
            # The .image setter already calls refresh(layout=True) internally
            self._img.image = pil_image
