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
    """Displays the PIL spirograph canvas scaled to fill the column width,
    with programmatic top-margin so it is always vertically centered."""

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

    # ── Core sizing & centering ───────────────────────────────────────────────

    def _render_and_center(self, pil_image: PILImage.Image) -> None:
        """Scale the PIL image to fill the column width, then set a
        top-margin so it sits vertically centered in the widget."""
        w_cells = self.size.width  or 80
        h_cells = self.size.height or 40
        cell    = _get_cell_size()

        # Fill the full column width.
        # For a square image, px_w / cell.height = img height in rows.
        # Cap at the container height so it never overflows vertically.
        px_w = w_cells * cell.width
        px_h = h_cells * cell.height
        px   = max(64, min(px_w, px_h))   # square image: take smaller dim

        img = pil_image.copy()
        img.thumbnail((px, px), PILImage.LANCZOS)

        # Vertical centering: compute how many rows the rendered image takes,
        # then push it down by half the remaining rows.
        img_rows  = max(1, round(img.height / cell.height))
        vpad      = max(0, (h_cells - img_rows) // 2)

        self._img.styles.margin_top    = vpad
        self._img.styles.margin_bottom = 0
        self._img.image = img

    # ── Public API ────────────────────────────────────────────────────────────

    def refresh_canvas(self, pil_image: PILImage.Image) -> None:
        if not (_HAS_TEXTUAL_IMAGE and hasattr(self, "_img")):
            return
        self._last_pil = pil_image
        self._render_and_center(pil_image)

    def on_resize(self, _event: events.Resize) -> None:
        if self._last_pil is not None and hasattr(self, "_img"):
            self._render_and_center(self._last_pil)
