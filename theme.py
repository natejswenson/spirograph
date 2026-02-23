# theme.py — single source of truth for all visual styling.
# Think of this like a CSS file: change values here to restyle the whole app.

# ── Core palette ─────────────────────────────────────────────────────────────
BG         = ( 15,  12,  28)
PANEL      = ( 22,  19,  42)
CARD       = ( 30,  26,  54)
CARD_EDGE  = ( 52,  48,  92)
TEXT       = (235, 232, 255)
TEXT_DIM   = (130, 122, 175)
CANVAS_BG  = (  8,   7,  17)

# ── Semantic / button colors ─────────────────────────────────────────────────
DRAW  = ( 99, 102, 241)   # indigo
UNDO  = (217, 119,   6)   # amber
CLEAR = (220,  38,  38)   # red
SAVE  = ( 22, 163,  74)   # green

# ── Per-slider accent colors ─────────────────────────────────────────────────
SLIDER_COLORS = [
    (129, 140, 248),   # Big Circle   — lavender
    (251, 113, 133),   # Little Wheel — pink
    ( 52, 211, 153),   # Pen Reach    — mint
    (251, 191,  36),   # Speed        — amber
    (167, 139, 250),   # Line Width   — purple
]

# ── Pen color presets ────────────────────────────────────────────────────────
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

# ── Card ─────────────────────────────────────────────────────────────────────
CARD_RADIUS    = 10
CARD_SHADOW_A  = 55     # shadow alpha

# ── Slider ───────────────────────────────────────────────────────────────────
SLIDER_ROW_H      = 44  # vertical space each slider occupies
SLIDER_TRACK_H    = 7
SLIDER_TRACK_R    = 4   # border-radius
SLIDER_HANDLE_R   = 11
SLIDER_GLOW_A     = 60  # handle glow alpha
SLIDER_INNER_TRIM = 3   # px trimmed from handle for white ring
SLIDER_CORE_TRIM  = 6   # px trimmed from handle for colored center

# ── Button ───────────────────────────────────────────────────────────────────
BTN_RADIUS       = 10
BTN_SHADOW_A     = 65
BTN_SHADOW_R     = 12
BTN_GLOSS_A      = 22   # top-half highlight alpha
BTN_HOVER_LERP   = 0.2  # animation speed per frame
BTN_HOVER_BOOST  = 55   # color brightness increase on hover
BTN_BORDER_W     = 1

# ── Color picker ─────────────────────────────────────────────────────────────
SWATCH_RADIUS        = 6
SWATCH_SEL_RADIUS    = 8
SWATCH_SEL_EXPAND    = 6    # inflate px for selection ring
RAINBOW_ACTIVE_COLOR = (252, 211, 40)
RAINBOW_CHECK_COLOR  = ( 20,  20,  20)

# ── Preview widget ────────────────────────────────────────────────────────────
PREVIEW_SPIN_IDLE    = 0.018   # radians per frame at rest
PREVIEW_SPIN_DRAW    = 0.055   # radians per frame while drawing
PREVIEW_GHOST_STEPS  = 900     # curve resolution for ghost trace
PREVIEW_GHOST_A      = 50      # ghost trace alpha
PREVIEW_MARGIN       = 10      # padding inside preview surface
PREVIEW_OUTER_RING   = ( 65,  60, 110)
PREVIEW_TICK         = ( 85,  80, 135)
PREVIEW_WHEEL_FILL   = ( 40,  38,  70)
PREVIEW_WHEEL_FILL_A = 180
PREVIEW_CROSSHAIR    = ( 70,  65, 110)
PREVIEW_PEN_ARM_A    = 200     # pen arm line alpha
PREVIEW_PEN_R        = 5       # outer pen dot radius
PREVIEW_PEN_RING_R   = 3       # white ring radius
PREVIEW_PEN_CORE_R   = 2       # colored center radius
PREVIEW_LABEL_LERP   = 0.4     # R= label color lerp toward white

# ── Canvas ───────────────────────────────────────────────────────────────────
CANVAS_BORDER_R      = 6
CANVAS_BORDER_W      = 2
CANVAS_GLOW_IDLE     = ( 48,  44,  88)
CANVAS_AURA_LAYERS   = [(16, 12), (9, 28), (3, 50)]  # (offset, alpha)

# ── Background canvas dot-grid ────────────────────────────────────────────────
GRID_SPACING         = 28
GRID_BASE_BRIGHT     = 20
GRID_VARY_AMP        = 7
GRID_VARY_FREQ       = 0.12
GRID_BLUE_TINT       = 10   # extra blue channel on dots

# ── Status bar ────────────────────────────────────────────────────────────────
STATUS_PULSE_FREQ    = 0.07   # sine frequency for pulsing dot
STATUS_DOT_R         = 6
STATUS_DOT_IDLE      = ( 55,  50,  88)
STATUS_PROGRESS_R    = 3      # progress bar border-radius

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_FACE_DEFAULT = "Arial"
FONT_FACE_MONO    = "Courier New"

FONT_SIZE_TITLE   = 15
FONT_SIZE_SECTION = 11
FONT_SIZE_LABEL   = 12
FONT_SIZE_VALUE   = 13
FONT_SIZE_BTN     = 13
FONT_SIZE_SMALL   = 11
