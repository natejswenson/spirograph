# constants.py — layout and geometry only.
# All visual styling (colors, radii, alphas, font sizes) lives in theme.py.
import os

SAVE_DIR = os.path.expanduser("~/Desktop/spirograph")
os.makedirs(SAVE_DIR, exist_ok=True)

WINDOW_W     = 1060
WINDOW_H     = 720
PANEL_W      = 330
CANVAS_SIZE  = 680
CANVAS_X     = PANEL_W + 25
CANVAS_Y     = (WINDOW_H - CANVAS_SIZE) // 2
PREVIEW_SIZE  = 155
CANVAS_MARGIN = 28   # padding between canvas edge and first drawn point
