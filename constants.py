import os

# ── Save directory ──────────────────────────────────────────────────────────────
SAVE_DIR = os.path.expanduser("~/Desktop/spirograph")
os.makedirs(SAVE_DIR, exist_ok=True)

# ── Layout ──────────────────────────────────────────────────────────────────────
WINDOW_W     = 1060
WINDOW_H     = 720
PANEL_W      = 330
CANVAS_SIZE  = 680
CANVAS_X     = PANEL_W + 25
CANVAS_Y     = (WINDOW_H - CANVAS_SIZE) // 2
PREVIEW_SIZE = 155

# ── Dark palette ────────────────────────────────────────────────────────────────
C_BG        = ( 15,  12,  28)
C_PANEL     = ( 22,  19,  42)
C_CARD      = ( 30,  26,  54)
C_CARD_EDGE = ( 52,  48,  92)
C_TEXT      = (235, 232, 255)
C_TEXT_DIM  = (130, 122, 175)
C_CANVAS_BG = (  8,   7,  17)

# ── Semantic button colors ───────────────────────────────────────────────────────
C_DRAW  = ( 99, 102, 241)
C_UNDO  = (217, 119,   6)
C_CLEAR = (220,  38,  38)
C_SAVE  = ( 22, 163,  74)

# ── Per-slider accent colors (one per slider) ────────────────────────────────────
SLIDER_COLORS = [
    (129, 140, 248),   # Big Circle   — lavender
    (251, 113, 133),   # Little Wheel — pink
    ( 52, 211, 153),   # Pen Reach    — mint
    (251, 191,  36),   # Speed        — amber
    (167, 139, 250),   # Line Width   — purple
]

# ── Color picker presets ─────────────────────────────────────────────────────────
PRESET_COLORS = [
    (255, 255, 255),
    (249,  87,  87),
    (252, 150,  55),
    (252, 215,  30),
    ( 60, 225, 120),
    ( 30, 210, 245),
    (105, 108, 255),
    (232,  75, 230),
]
