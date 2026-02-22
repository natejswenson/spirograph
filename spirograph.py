import pygame
import math
import colorsys
import os
from datetime import datetime

# ── Save directory ──────────────────────────────────────────────────────────────
SAVE_DIR = os.path.expanduser("~/Desktop/spirograph")
os.makedirs(SAVE_DIR, exist_ok=True)

# ── Layout ──────────────────────────────────────────────────────────────────────
WINDOW_W, WINDOW_H = 1060, 720
PANEL_W   = 330
CANVAS_SIZE = 680
CANVAS_X  = PANEL_W + 25
CANVAS_Y  = (WINDOW_H - CANVAS_SIZE) // 2

PREVIEW_SIZE = 170   # px — mechanism preview widget

# ── Palette ─────────────────────────────────────────────────────────────────────
C_BG        = ( 15,  12,  28)
C_PANEL     = ( 22,  19,  42)
C_CARD      = ( 30,  26,  54)
C_CARD_EDGE = ( 52,  48,  92)
C_TEXT      = (235, 232, 255)
C_TEXT_DIM  = (130, 122, 175)
C_CANVAS_BG = (  8,   7,  17)

C_DRAW  = ( 99, 102, 241)
C_UNDO  = (217, 119,   6)
C_CLEAR = (220,  38,  38)
C_SAVE  = ( 22, 163,  74)

# Per-slider accent colors
SLIDER_COLORS = [
    (129, 140, 248),   # Big Circle
    (251, 113, 133),   # Little Wheel
    ( 52, 211, 153),   # Pen Reach
    (251, 191,  36),   # Speed
    (167, 139, 250),   # Line Width
]

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

# ── Helpers ──────────────────────────────────────────────────────────────────────
def gcd(a, b):
    a, b = int(round(a)), int(round(b))
    while b:
        a, b = b, a % b
    return a

def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

pygame.font.init()

def load_fonts():
    return {
        "title":   pygame.font.SysFont("Arial", 15, bold=True),
        "section": pygame.font.SysFont("Arial", 11, bold=True),
        "label":   pygame.font.SysFont("Arial", 12, bold=True),
        "value":   pygame.font.SysFont("Courier New", 13, bold=True),
        "btn":     pygame.font.SysFont("Arial", 13, bold=True),
        "small":   pygame.font.SysFont("Arial", 11),
    }

def draw_card(surface, rect, color=C_CARD, edge=C_CARD_EDGE, radius=10):
    sh = pygame.Surface((rect.w + 4, rect.h + 5), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 55), sh.get_rect(), border_radius=radius + 2)
    surface.blit(sh, (rect.x - 1, rect.y + 3))
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    pygame.draw.rect(surface, edge, rect, 1, border_radius=radius)


# ── Mechanism Preview Widget ─────────────────────────────────────────────────────
class PreviewWidget:
    """Animated physical toy preview: outer ring, rolling inner wheel, pen dot,
    ghost trace of the full curve."""

    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self._angle = 0.0          # rolling angle of inner wheel
        self._ghost_pts  = []      # precomputed ghost curve points (scaled)
        self._ghost_params = None  # (R, r, d) cache key
        self._spiro = _Spiro()

    def update(self, drawing):
        # Rotate faster while drawing, slow idle spin otherwise
        self._angle += 0.018 if not drawing else 0.055

    def _get_ghost(self, R, r, d):
        params = (R, r, d)
        if params == self._ghost_params:
            return self._ghost_pts
        self._ghost_params = params
        raw = self._spiro.compute_points(R, r, d, steps=900)
        max_ext = max(max(abs(px) for px, _ in raw),
                      max(abs(py) for _, py in raw), 1)
        pad   = self.size * 0.5 - 10
        scale = pad / max_ext
        cx = cy = self.size // 2
        self._ghost_pts = [(cx + px * scale, cy + py * scale) for px, py in raw]
        return self._ghost_pts

    def draw(self, surface, R, r, d, pen_color, fonts):
        sz = self.size
        # Everything is drawn into a local sz×sz surface so all
        # coordinates are in the range [0, sz] with center = (sz//2, sz//2).
        local = pygame.Surface((sz, sz), pygame.SRCALPHA)
        cx = cy = sz // 2

        max_r = R + 4
        scale = (sz // 2 - 10) / max_r

        # ── Ghost trace (already in local coords) ──
        ghost = self._get_ghost(R, r, d)
        if len(ghost) > 1:
            pts = [(int(px), int(py)) for px, py in ghost]
            pygame.draw.lines(local, (*pen_color[:3], 50), False, pts, 1)

        # ── Outer ring ──
        R_px = int(R * scale)
        pygame.draw.circle(local, (65, 60, 110), (cx, cy), R_px, 2)
        for i in range(12):
            a = i * math.pi / 6
            pygame.draw.line(local, (85, 80, 135),
                             (cx + int((R_px - 5) * math.cos(a)),
                              cy + int((R_px - 5) * math.sin(a))),
                             (cx + int(R_px * math.cos(a)),
                              cy + int(R_px * math.sin(a))), 1)

        # ── Inner wheel ──
        r_clamped = min(r, R - 1)
        wx = cx + int((R - r_clamped) * scale * math.cos(self._angle))
        wy = cy + int((R - r_clamped) * scale * math.sin(self._angle))
        r_px = max(2, int(r_clamped * scale))

        wheel_fill = pygame.Surface((r_px * 2 + 2, r_px * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(wheel_fill, (40, 38, 70, 180), (r_px + 1, r_px + 1), r_px)
        local.blit(wheel_fill, (wx - r_px - 1, wy - r_px - 1))

        pygame.draw.circle(local, SLIDER_COLORS[1], (wx, wy), r_px, 2)
        inner_rot = -(R - r_clamped) / max(r_clamped, 0.001) * self._angle
        gear_count = max(4, int(r_clamped / 12))
        for i in range(gear_count):
            ga = inner_rot + i * (2 * math.pi / gear_count)
            pygame.draw.circle(local, SLIDER_COLORS[1],
                               (wx + int((r_px - 3) * math.cos(ga)),
                                wy + int((r_px - 3) * math.sin(ga))), 2)

        pygame.draw.line(local, (70, 65, 110),
                         (wx - r_px + 4, wy), (wx + r_px - 4, wy), 1)
        pygame.draw.line(local, (70, 65, 110),
                         (wx, wy - r_px + 4), (wx, wy + r_px - 4), 1)

        # ── Pen arm + dot ──
        px2 = wx + int(d * scale * math.cos(inner_rot))
        py2 = wy + int(d * scale * math.sin(inner_rot))
        pygame.draw.line(local, (*SLIDER_COLORS[2], 200), (wx, wy), (px2, py2), 2)
        pygame.draw.circle(local, pen_color,       (px2, py2), 5)
        pygame.draw.circle(local, (255, 255, 255), (px2, py2), 3)
        pygame.draw.circle(local, pen_color,       (px2, py2), 2)

        # ── Labels ──
        f = fonts["small"]
        lbl_R = f.render(f"R={R}", True, lerp_color(SLIDER_COLORS[0], (200, 200, 255), 0.4))
        local.blit(lbl_R, (cx - lbl_R.get_width() // 2, sz - 16))
        lbl_r = f.render(f"r={r}", True, SLIDER_COLORS[1])
        local.blit(lbl_r, (min(wx + r_px + 3, sz - lbl_r.get_width() - 2), wy - 7))

        # Blit the finished local surface onto the panel
        surface.blit(local, (self.x, self.y))


# ── Slider ───────────────────────────────────────────────────────────────────────
class Slider:
    TRACK_H  = 7
    HANDLE_R = 11
    ROW_H    = 48

    def __init__(self, x, y, w, mn, mx, init, emoji, label, color, fonts):
        self.track   = pygame.Rect(x, y + 30, w, self.TRACK_H)
        self.min_val = mn
        self.max_val = mx
        self._value  = float(init)
        self.emoji   = emoji
        self.label   = label
        self.color   = color
        self.fonts   = fonts
        self.dragging = False

    @property
    def value(self):
        return int(round(self._value))

    def _vx(self, val):
        r = (val - self.min_val) / (self.max_val - self.min_val)
        return self.track.x + int(r * self.track.w)

    def _xv(self, x):
        return self.min_val + clamp((x - self.track.x) / self.track.w, 0, 1) * (self.max_val - self.min_val)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            hx = self._vx(self._value)
            if (math.hypot(event.pos[0] - hx, event.pos[1] - self.track.centery) <= self.HANDLE_R + 6
                    or self.track.inflate(0, 26).collidepoint(event.pos)):
                self.dragging = True
                self._value = self._xv(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._value = self._xv(event.pos[0])
            return True
        return False

    def draw(self, surface):
        f  = self.fonts
        hx = self._vx(self._value)

        em  = f["label"].render(f"{self.emoji}  {self.label}", True, C_TEXT)
        val = f["value"].render(str(self.value), True, self.color)
        surface.blit(em,  (self.track.x, self.track.y - 18))
        surface.blit(val, (self.track.right - val.get_width(), self.track.y - 19))

        # Track bg
        tr = pygame.Rect(self.track.x, self.track.centery - self.TRACK_H // 2,
                         self.track.w, self.TRACK_H)
        pygame.draw.rect(surface, C_CARD_EDGE, tr, border_radius=4)

        # Fill
        fw = hx - self.track.x
        if fw > 0:
            pygame.draw.rect(surface, self.color,
                             pygame.Rect(tr.x, tr.y, fw, tr.h), border_radius=4)

        # Glow behind handle
        r = self.HANDLE_R
        glow = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 60), (r * 2, r * 2), r * 2)
        surface.blit(glow, (hx - r * 2, self.track.centery - r * 2))

        # Handle
        pygame.draw.circle(surface, self.color,         (hx, self.track.centery), r)
        pygame.draw.circle(surface, (255, 255, 255),    (hx, self.track.centery), r - 3)
        pygame.draw.circle(surface, self.color,         (hx, self.track.centery), r - 6)


# ── Button ───────────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, x, y, w, h, icon, text, color, fonts):
        self.rect  = pygame.Rect(x, y, w, h)
        self.icon  = icon
        self.text  = text
        self.color = color
        self.fonts = fonts
        self._t    = 0.0

    def draw(self, surface, hovered):
        self._t += ((1.0 if hovered else 0.0) - self._t) * 0.2
        col = lerp_color(self.color, tuple(min(255, c + 55) for c in self.color), self._t)

        sh = pygame.Surface((self.rect.w + 4, self.rect.h + 6), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 65), sh.get_rect(), border_radius=12)
        surface.blit(sh, (self.rect.x - 1, self.rect.y + 4))

        pygame.draw.rect(surface, col, self.rect, border_radius=10)

        gloss = pygame.Surface((self.rect.w - 4, self.rect.h // 2 - 2), pygame.SRCALPHA)
        gloss.fill((255, 255, 255, 22))
        surface.blit(gloss, (self.rect.x + 2, self.rect.y + 2))

        pygame.draw.rect(surface, C_CARD_EDGE, self.rect, 1, border_radius=10)

        label = f"{self.icon}  {self.text}"
        lbl = self.fonts["btn"].render(label, True, (255, 255, 255))
        surface.blit(lbl, lbl.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# ── Color picker ─────────────────────────────────────────────────────────────────
class ColorPicker:
    SW  = 26
    GAP = 6

    def __init__(self, x, y, fonts):
        self.x = x
        self.y = y
        self.selected = 0
        self.rainbow  = False
        self.fonts    = fonts
        self._build()

    def _build(self):
        self.rects = []
        # Single row of 8
        for i in range(len(PRESET_COLORS)):
            rx = self.x + i * (self.SW + self.GAP)
            self.rects.append(pygame.Rect(rx, self.y, self.SW, self.SW))
        rb_y = self.y + self.SW + 10
        self.rb_rect = pygame.Rect(self.x, rb_y, 16, 16)
        self.rb_pos  = (self.x + 22, rb_y + 1)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self.rects):
                if r.collidepoint(event.pos):
                    self.selected = i
                    self.rainbow  = False
                    return True
            if self.rb_rect.collidepoint(event.pos):
                self.rainbow = not self.rainbow
                return True
        return False

    def get_color(self, idx, total):
        if self.rainbow:
            h = (idx / max(total, 1)) % 1.0
            r, g, b = colorsys.hsv_to_rgb(h, 1.0, 1.0)
            return (int(r * 255), int(g * 255), int(b * 255))
        return PRESET_COLORS[self.selected]

    def current_solid(self):
        return PRESET_COLORS[self.selected]

    def draw(self, surface):
        lbl = self.fonts["section"].render("🎨  Color", True, C_TEXT_DIM)
        surface.blit(lbl, (self.x, self.y - 18))

        for i, (r, col) in enumerate(zip(self.rects, PRESET_COLORS)):
            if i == self.selected and not self.rainbow:
                ring = r.inflate(6, 6)
                pygame.draw.rect(surface, col, ring, border_radius=8)
            pygame.draw.rect(surface, col, r, border_radius=6)

        rb_col = (252, 211, 40) if self.rainbow else C_CARD_EDGE
        pygame.draw.rect(surface, rb_col, self.rb_rect, border_radius=3)
        pygame.draw.rect(surface, C_TEXT_DIM, self.rb_rect, 1, border_radius=3)
        if self.rainbow:
            ck = self.fonts["small"].render("✓", True, (20, 20, 20))
            surface.blit(ck, ck.get_rect(center=self.rb_rect.center))
        lbl2 = self.fonts["label"].render("🌈  Rainbow!",
                                          True, (252, 211, 40) if self.rainbow else C_TEXT_DIM)
        surface.blit(lbl2, self.rb_pos)


# ── Spirograph math ───────────────────────────────────────────────────────────────
class _Spiro:
    def get_period(self, R, r):
        ri = max(1, int(round(r)))
        Ri = max(1, int(round(R)))
        return ri // max(1, gcd(Ri, ri))

    def compute_points(self, R, r, d, steps=6000):
        loops   = self.get_period(R, r)
        total_t = 2 * math.pi * loops
        pts = []
        for i in range(steps + 1):
            t = total_t * i / steps
            x = (R - r) * math.cos(t) + d * math.cos((R - r) * t / max(r, 0.001))
            y = (R - r) * math.sin(t) - d * math.sin((R - r) * t / max(r, 0.001))
            pts.append((x, y))
        return pts


# ── Canvas dot-grid background ────────────────────────────────────────────────────
def make_canvas_bg(size):
    surf = pygame.Surface((size, size))
    surf.fill(C_CANVAS_BG)
    for gx in range(28, size, 28):
        for gy in range(28, size, 28):
            c = 20 + int(7 * math.sin(gx * 0.12) * math.cos(gy * 0.12))
            surf.set_at((gx, gy), (c, c, c + 10))
    return surf


# ── App ───────────────────────────────────────────────────────────────────────────
class App:
    MAX_UNDO = 20

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("Spirograph Studio")
        self.fonts = load_fonts()

        self._canvas_bg = make_canvas_bg(CANVAS_SIZE)
        self.canvas     = self._canvas_bg.copy()

        self.spiro       = _Spiro()
        self.drawing     = False
        self.draw_index  = 0
        self.draw_points = []
        self.draw_total  = 0
        self.layer_count = 0
        self._undo_stack = []
        self._tick       = 0
        self._save_flash = 0

        self.clock = pygame.time.Clock()
        self._build_ui()

    def _build_ui(self):
        f  = self.fonts
        px = 16
        sw = PANEL_W - px * 2 - 12

        # ── Preview card ──
        preview_card_y = 48
        preview_card_h = PREVIEW_SIZE + 28
        self._preview_card = pygame.Rect(6, preview_card_y, PANEL_W - 6, preview_card_h)
        pw_x = (PANEL_W - PREVIEW_SIZE) // 2
        pw_y = preview_card_y + 14
        self.preview = PreviewWidget(pw_x, pw_y, PREVIEW_SIZE)

        # ── Sliders card ──
        sliders_card_y = preview_card_y + preview_card_h + 8
        y = sliders_card_y + 28
        defs = [
            ("⭕", "Big Circle",   50, 300, 150, SLIDER_COLORS[0]),
            ("🔵", "Little Wheel",  5, 200,  80, SLIDER_COLORS[1]),
            ("✏️", "Pen Reach",     5, 250, 100, SLIDER_COLORS[2]),
            ("⚡", "Speed",         1,  20,   5, SLIDER_COLORS[3]),
            ("📏", "Line Width",    1,   8,   1, SLIDER_COLORS[4]),
        ]
        self.sliders = []
        for em, lb, mn, mx, init, col in defs:
            self.sliders.append(Slider(px, y, sw, mn, mx, init, em, lb, col, f))
            y += Slider.ROW_H
        sliders_card_h = y - sliders_card_y + 10
        self._sliders_card = pygame.Rect(6, sliders_card_y, PANEL_W - 6, sliders_card_h)

        # ── Color card ──
        color_card_y = sliders_card_y + sliders_card_h + 8
        self.color_picker = ColorPicker(px, color_card_y + 30, f)
        color_card_h = ColorPicker.SW + 46
        self._color_card = pygame.Rect(6, color_card_y, PANEL_W - 6, color_card_h)

        # ── Buttons card ──
        btn_card_y = color_card_y + color_card_h + 8
        by = btn_card_y + 10
        bw  = PANEL_W - 6 - px * 2 + 4
        bh  = 36
        bhalf = (bw - 6) // 2
        self.btn_draw  = Button(px, by, bw,    bh, "▶", "Draw",  C_DRAW,  f); by += bh + 6
        self.btn_undo  = Button(px, by, bhalf, bh, "↩", "Undo",  C_UNDO,  f)
        self.btn_clear = Button(px + bhalf + 6, by, bhalf, bh, "✕", "Clear", C_CLEAR, f); by += bh + 6
        self.btn_save  = Button(px, by, bw, bh, "💾", "Save PNG", C_SAVE, f); by += bh + 10
        self._btn_card = pygame.Rect(6, btn_card_y, PANEL_W - 6, by - btn_card_y)

        self.buttons = [self.btn_draw, self.btn_undo, self.btn_clear, self.btn_save]

    # ── Undo ──────────────────────────────────────────────────────────────────────
    def _push_undo(self):
        self._undo_stack.append(self.canvas.copy())
        if len(self._undo_stack) > self.MAX_UNDO:
            self._undo_stack.pop(0)

    def _pop_undo(self):
        if self._undo_stack:
            self.drawing     = False
            self.canvas      = self._undo_stack.pop()
            self.layer_count = max(0, self.layer_count - 1)

    # ── Drawing ───────────────────────────────────────────────────────────────────
    def _R(self): return self.sliders[0].value
    def _r(self): return min(self.sliders[1].value, self._R() - 1)
    def _d(self): return self.sliders[2].value

    def start_drawing(self):
        R, r, d = self._R(), self._r(), self._d()
        pts = self.spiro.compute_points(R, r, d)
        max_ext = max(max(abs(x) for x, _ in pts),
                      max(abs(y) for _, y in pts), 1)
        scale = (CANVAS_SIZE / 2 - 28) / max_ext
        cx = cy = CANVAS_SIZE // 2
        self.draw_points = [(cx + x * scale, cy + y * scale) for x, y in pts]
        self.draw_total  = len(self.draw_points)
        self.draw_index  = 1
        self._push_undo()
        self.drawing = True

    def _animate_step(self):
        if not self.drawing:
            return
        speed = self.sliders[3].value * 5
        thick = self.sliders[4].value
        cp    = self.color_picker
        for _ in range(speed):
            if self.draw_index >= self.draw_total:
                self.drawing     = False
                self.layer_count += 1
                break
            p1 = self.draw_points[self.draw_index - 1]
            p2 = self.draw_points[self.draw_index]
            col = cp.get_color(self.draw_index, self.draw_total)
            pygame.draw.line(self.canvas, col,
                             (int(p1[0]), int(p1[1])),
                             (int(p2[0]), int(p2[1])), thick)
            self.draw_index += 1

    # ── Render ────────────────────────────────────────────────────────────────────
    def _draw_panel(self, mouse):
        self._tick += 1
        panel = pygame.Surface((PANEL_W, WINDOW_H))
        panel.fill(C_PANEL)

        # Title bar
        pygame.draw.rect(panel, C_CARD, pygame.Rect(0, 0, PANEL_W, 44))
        pygame.draw.line(panel, C_CARD_EDGE, (0, 44), (PANEL_W, 44))

        pulse = 0.5 + 0.5 * math.sin(self._tick * 0.07)
        dot_c = lerp_color((70, 65, 110), C_DRAW, pulse) if self.drawing else (55, 50, 88)
        pygame.draw.circle(panel, dot_c, (16, 22), 6)

        title = self.fonts["title"].render("SPIROGRAPH STUDIO", True, C_TEXT)
        panel.blit(title, (28, 14))

        # Preview card
        draw_card(panel, self._preview_card)
        sec = self.fonts["section"].render("👁  Preview", True, C_TEXT_DIM)
        panel.blit(sec, (self._preview_card.x + 10, self._preview_card.y + 8))
        pen_col = self.color_picker.current_solid()
        self.preview.update(self.drawing)
        self.preview.draw(panel, self._R(), self._r(), self._d(), pen_col, self.fonts)

        # Sliders card
        draw_card(panel, self._sliders_card)
        sec2 = self.fonts["section"].render("🎛  Adjust the Shape", True, C_TEXT_DIM)
        panel.blit(sec2, (self._sliders_card.x + 10, self._sliders_card.y + 8))
        for s in self.sliders:
            s.draw(panel)

        # Color card
        draw_card(panel, self._color_card)
        self.color_picker.draw(panel)

        # Button card
        draw_card(panel, self._btn_card)
        for btn in self.buttons:
            btn.draw(panel, btn.rect.collidepoint(mouse))

        # Status strip
        sy = WINDOW_H - 30
        pygame.draw.line(panel, C_CARD_EDGE, (0, sy), (PANEL_W, sy))
        if self.drawing:
            pct = self.draw_index / max(self.draw_total, 1)
            bar = pygame.Rect(8, sy + 8, PANEL_W - 16, 6)
            pygame.draw.rect(panel, C_CARD_EDGE, bar, border_radius=3)
            fw  = int(bar.w * pct)
            if fw > 0:
                pygame.draw.rect(panel, C_DRAW,
                                 pygame.Rect(bar.x, bar.y, fw, bar.h), border_radius=3)
            t = self.fonts["small"].render(f"Drawing…  {int(pct * 100)}%", True, C_TEXT_DIM)
            panel.blit(t, (10, sy + 16))
        elif self._save_flash > 0:
            self._save_flash -= 1
            t = self.fonts["small"].render("✓  Saved to Desktop/spirograph", True, C_SAVE)
            panel.blit(t, (10, sy + 8))
        else:
            t = self.fonts["small"].render(
                f"Layers: {self.layer_count}   Undo: {len(self._undo_stack)}", True, C_TEXT_DIM)
            panel.blit(t, (10, sy + 8))

        pygame.draw.line(panel, C_CARD_EDGE, (PANEL_W - 1, 0), (PANEL_W - 1, WINDOW_H))
        self.screen.blit(panel, (0, 0))

    def _draw_canvas(self):
        # Glow aura
        for offset, alpha in ((16, 12), (9, 28), (3, 50)):
            aura = pygame.Surface((CANVAS_SIZE + offset * 2, CANVAS_SIZE + offset * 2),
                                  pygame.SRCALPHA)
            col  = C_DRAW if self.drawing else (48, 44, 88)
            pygame.draw.rect(aura, (*col, alpha), aura.get_rect(), border_radius=10 + offset)
            self.screen.blit(aura, (CANVAS_X - offset, CANVAS_Y - offset))

        pygame.draw.rect(self.screen, C_CARD_EDGE,
                         pygame.Rect(CANVAS_X - 2, CANVAS_Y - 2,
                                     CANVAS_SIZE + 4, CANVAS_SIZE + 4),
                         2, border_radius=6)
        self.screen.blit(self.canvas, (CANVAS_X, CANVAS_Y))

    # ── Main loop ─────────────────────────────────────────────────────────────────
    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            mouse = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_z and (event.mod & pygame.KMOD_META
                                                      or event.mod & pygame.KMOD_CTRL):
                        self._pop_undo()

                handled = False
                for s in self.sliders:
                    if s.handle_event(event):
                        handled = True
                if not handled:
                    self.color_picker.handle_event(event)

                if self.btn_draw.is_clicked(event):
                    self.start_drawing()
                elif self.btn_undo.is_clicked(event):
                    self._pop_undo()
                elif self.btn_clear.is_clicked(event):
                    self._push_undo()
                    self.drawing     = False
                    self.canvas      = self._canvas_bg.copy()
                    self.layer_count = 0
                elif self.btn_save.is_clicked(event):
                    ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
                    fname = os.path.join(SAVE_DIR, f"spirograph_{ts}.png")
                    pygame.image.save(self.canvas, fname)
                    self._save_flash = 120

            self._animate_step()
            self.screen.fill(C_BG)
            self._draw_panel(mouse)
            self._draw_canvas()
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    App().run()
