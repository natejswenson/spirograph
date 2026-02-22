import pygame
import pygame.gfxdraw
import math
import colorsys
import os
from datetime import datetime

# ── Save directory ──────────────────────────────────────────────────────────────
SAVE_DIR = os.path.expanduser("~/Desktop/spirograph")
os.makedirs(SAVE_DIR, exist_ok=True)

# ── Layout ──────────────────────────────────────────────────────────────────────
WINDOW_W, WINDOW_H = 980, 700
PANEL_W = 300
CANVAS_SIZE = 660
CANVAS_X = PANEL_W + 10
CANVAS_Y = (WINDOW_H - CANVAS_SIZE) // 2

# ── Palette ─────────────────────────────────────────────────────────────────────
C_BG           = ( 12,  13,  20)   # near-black
C_PANEL        = ( 20,  22,  35)   # panel bg
C_PANEL_EDGE   = ( 38,  42,  68)   # panel border
C_CANVAS_BG    = (  8,   9,  16)   # canvas dark
C_TEXT         = (210, 215, 235)   # primary text
C_TEXT_DIM     = (110, 118, 155)   # secondary text
C_ACCENT       = ( 99, 102, 241)   # indigo accent
C_ACCENT_LO    = ( 55,  58, 150)   # dim accent
C_HANDLE       = (200, 205, 255)   # slider handle
C_TRACK        = ( 38,  42,  68)   # slider track
C_TRACK_FILL   = ( 79,  82, 200)   # slider filled
C_SUCCESS      = ( 52, 199, 120)   # save / success green
C_DANGER       = (239,  68,  68)   # clear red
C_UNDO         = (234, 179,   8)   # undo yellow
C_DIVIDER      = ( 38,  42,  68)

PRESET_COLORS = [
    (255, 255, 255),
    (248,  84,  84),
    (251, 146,  60),
    (250, 204,  21),
    ( 74, 222, 128),
    ( 34, 211, 238),
    ( 99, 102, 241),
    (232,  77, 232),
]

# ── Helpers ──────────────────────────────────────────────────────────────────────
def gcd(a, b):
    a, b = int(round(a)), int(round(b))
    while b:
        a, b = b, a % b
    return a

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

pygame.font.init()

def load_fonts():
    return {
        "title":  pygame.font.SysFont("Arial", 17, bold=True),
        "label":  pygame.font.SysFont("Arial", 12),
        "value":  pygame.font.SysFont("Courier New", 12, bold=True),
        "btn":    pygame.font.SysFont("Arial", 13, bold=True),
        "small":  pygame.font.SysFont("Arial", 11),
        "status": pygame.font.SysFont("Arial", 11),
    }

# ── Slider ───────────────────────────────────────────────────────────────────────
class Slider:
    H = 4        # track height
    HR = 8       # handle radius
    ROW = 44     # total row height

    def __init__(self, x, y, w, min_val, max_val, initial, label, fonts):
        self.rect = pygame.Rect(x, y + 20, w, self.H)
        self.min_val = min_val
        self.max_val = max_val
        self._value = float(initial)
        self.label = label
        self.fonts = fonts
        self.dragging = False

    @property
    def value(self):
        return int(round(self._value))

    def _val_to_x(self, val):
        r = (val - self.min_val) / (self.max_val - self.min_val)
        return self.rect.x + int(r * self.rect.w)

    def _x_to_val(self, x):
        r = clamp((x - self.rect.x) / self.rect.w, 0.0, 1.0)
        return self.min_val + r * (self.max_val - self.min_val)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            hx = self._val_to_x(self._value)
            hit_handle = math.hypot(event.pos[0] - hx,
                                    event.pos[1] - self.rect.centery) <= self.HR + 4
            hit_track = self.rect.inflate(0, 24).collidepoint(event.pos)
            if hit_handle or hit_track:
                self.dragging = True
                self._value = self._x_to_val(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._value = self._x_to_val(event.pos[0])
            return True
        return False

    def draw(self, surface):
        # Label + value on same line
        lbl = self.fonts["label"].render(self.label, True, C_TEXT_DIM)
        val = self.fonts["value"].render(str(self.value), True, C_HANDLE)
        surface.blit(lbl, (self.rect.x, self.rect.y - 18))
        surface.blit(val, (self.rect.right - val.get_width(), self.rect.y - 18))

        # Track background
        tr = pygame.Rect(self.rect.x, self.rect.centery - self.H // 2,
                         self.rect.w, self.H)
        pygame.draw.rect(surface, C_TRACK, tr, border_radius=2)

        # Filled track
        hx = self._val_to_x(self._value)
        fill_w = hx - self.rect.x
        if fill_w > 0:
            fr = pygame.Rect(self.rect.x, self.rect.centery - self.H // 2,
                             fill_w, self.H)
            pygame.draw.rect(surface, C_TRACK_FILL, fr, border_radius=2)

        # Handle: outer glow ring + filled circle
        glow_r = self.HR + 3
        s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*C_ACCENT, 60), (glow_r, glow_r), glow_r)
        surface.blit(s, (hx - glow_r, self.rect.centery - glow_r))
        pygame.draw.circle(surface, C_ACCENT, (hx, self.rect.centery), self.HR)
        pygame.draw.circle(surface, C_HANDLE, (hx, self.rect.centery), self.HR - 2)


# ── Button ───────────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, x, y, w, h, text, color, fonts):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.fonts = fonts
        self._hover_t = 0.0   # 0..1 lerp for hover animation

    def draw(self, surface, hovered):
        target = 1.0 if hovered else 0.0
        self._hover_t += (target - self._hover_t) * 0.25
        t = self._hover_t

        base = lerp_color(self.color, tuple(min(255, c + 40) for c in self.color), t)

        # Shadow
        shadow = pygame.Rect(self.rect.x + 2, self.rect.y + 3,
                             self.rect.w, self.rect.h)
        pygame.draw.rect(surface, (0, 0, 0, 80), shadow, border_radius=8)

        # Body
        pygame.draw.rect(surface, base, self.rect, border_radius=8)

        # Top highlight stripe
        hi = pygame.Rect(self.rect.x + 2, self.rect.y + 2,
                         self.rect.w - 4, self.rect.h // 2 - 2)
        hs = pygame.Surface((hi.w, hi.h), pygame.SRCALPHA)
        hs.fill((255, 255, 255, 18))
        surface.blit(hs, hi.topleft)

        # Border
        border_col = lerp_color(C_PANEL_EDGE, C_HANDLE, t * 0.5)
        pygame.draw.rect(surface, border_col, self.rect, 1, border_radius=8)

        lbl = self.fonts["btn"].render(self.text, True, (255, 255, 255))
        surface.blit(lbl, lbl.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


# ── ColorPicker ──────────────────────────────────────────────────────────────────
class ColorPicker:
    SW = 26
    GAP = 6

    def __init__(self, x, y, fonts):
        self.x = x
        self.y = y
        self.selected = 0
        self.rainbow = False
        self.fonts = fonts
        self._build()

    def _build(self):
        self.rects = []
        for i in range(len(PRESET_COLORS)):
            col = i % 4
            row = i // 4
            rx = self.x + col * (self.SW + self.GAP)
            ry = self.y + row * (self.SW + self.GAP)
            self.rects.append(pygame.Rect(rx, ry, self.SW, self.SW))
        rb_y = self.y + 2 * (self.SW + self.GAP) + 8
        self.rb_rect = pygame.Rect(self.x, rb_y, 16, 16)
        self.rb_label_pos = (self.x + 22, rb_y)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self.rects):
                if r.collidepoint(event.pos):
                    self.selected = i
                    self.rainbow = False
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

    def draw(self, surface):
        lbl = self.fonts["label"].render("Color", True, C_TEXT_DIM)
        surface.blit(lbl, (self.x, self.y - 18))

        for i, (r, col) in enumerate(zip(self.rects, PRESET_COLORS)):
            # Draw swatch with rounded corners
            pygame.draw.rect(surface, col, r, border_radius=5)
            if i == self.selected and not self.rainbow:
                # White ring
                pygame.draw.rect(surface, (255, 255, 255), r, 2, border_radius=5)
                # Inner accent dot
                pygame.draw.circle(surface, (255, 255, 255),
                                   r.center, 4)
                pygame.draw.circle(surface, col, r.center, 3)
            else:
                pygame.draw.rect(surface, C_TRACK, r, 1, border_radius=5)

        # Rainbow toggle
        rb_col = (250, 200, 30) if self.rainbow else C_TRACK
        pygame.draw.rect(surface, rb_col, self.rb_rect, border_radius=3)
        pygame.draw.rect(surface, C_PANEL_EDGE, self.rb_rect, 1, border_radius=3)
        if self.rainbow:
            ck = self.fonts["small"].render("✓", True, (20, 20, 20))
            surface.blit(ck, ck.get_rect(center=self.rb_rect.center))
        lbl2 = self.fonts["label"].render("Rainbow", True, C_TEXT)
        surface.blit(lbl2, self.rb_label_pos)


# ── Spirograph math ───────────────────────────────────────────────────────────────
class Spirograph:
    def get_period(self, R, r):
        ri = max(1, int(round(r)))
        Ri = max(1, int(round(R)))
        g = gcd(Ri, ri)
        return ri // g

    def compute_points(self, R, r, d, steps=6000):
        loops = self.get_period(R, r)
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
    dot_col = (22, 26, 44)
    spacing = 30
    for gx in range(spacing, size, spacing):
        for gy in range(spacing, size, spacing):
            surf.set_at((gx, gy), dot_col)
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
        self.canvas = self._canvas_bg.copy()

        self.spiro = Spirograph()
        self.drawing = False
        self.draw_index = 0
        self.draw_points = []
        self.draw_total = 0
        self.layer_count = 0

        # Undo stack: list of Surface copies
        self._undo_stack = []

        self.clock = pygame.time.Clock()
        self._anim_tick = 0   # used for pulsing effects
        self._build_ui()

    def _build_ui(self):
        f = self.fonts
        px, sw = 22, PANEL_W - 22 - 36
        y = 58

        self.sl_R     = Slider(px, y, sw, 50, 300, 150, "R  outer radius", f); y += 50
        self.sl_r     = Slider(px, y, sw,  5, 200,  80, "r  inner radius", f); y += 50
        self.sl_d     = Slider(px, y, sw,  5, 250, 100, "d  pen offset",   f); y += 50
        self.sl_speed = Slider(px, y, sw,  1,  20,   5, "Speed",           f); y += 50
        self.sl_thick = Slider(px, y, sw,  1,   8,   1, "Thickness",       f); y += 58

        self.color_picker = ColorPicker(px, y + 20, f); y += 105

        bw, bh = PANEL_W - px * 2, 36
        self.btn_draw  = Button(px, y, bw, bh, "▶  Draw",     C_ACCENT,  f); y += bh + 8
        self.btn_undo  = Button(px, y, bw, bh, "↩  Undo",     (120, 90, 10), f); y += bh + 8
        self.btn_clear = Button(px, y, bw, bh, "✕  Clear",    (90, 35, 35),  f); y += bh + 8
        self.btn_save  = Button(px, y, bw, bh, "⬇  Save PNG", (30, 90, 55),  f)

        self.sliders = [self.sl_R, self.sl_r, self.sl_d, self.sl_speed, self.sl_thick]
        self.buttons = [self.btn_draw, self.btn_undo, self.btn_clear, self.btn_save]

    # ── Undo ──────────────────────────────────────────────────────────────────────
    def _push_undo(self):
        self._undo_stack.append(self.canvas.copy())
        if len(self._undo_stack) > self.MAX_UNDO:
            self._undo_stack.pop(0)

    def _pop_undo(self):
        if self._undo_stack:
            self.drawing = False
            self.canvas = self._undo_stack.pop()
            self.layer_count = max(0, self.layer_count - 1)

    # ── Drawing ───────────────────────────────────────────────────────────────────
    def _clamp_r(self):
        R, r = self.sl_R.value, self.sl_r.value
        return min(r, R - 1) if r >= R else r

    def start_drawing(self):
        R, r, d = self.sl_R.value, self._clamp_r(), self.sl_d.value
        pts = self.spiro.compute_points(R, r, d)

        max_ext = max((max(abs(x) for x, _ in pts),
                       max(abs(y) for _, y in pts),
                       1))
        scale = (CANVAS_SIZE / 2 - 24) / max_ext
        cx = cy = CANVAS_SIZE // 2
        self.draw_points = [(cx + x * scale, cy + y * scale) for x, y in pts]
        self.draw_total = len(self.draw_points)
        self.draw_index = 1

        self._push_undo()
        self.drawing = True

    def _animate_step(self):
        if not self.drawing:
            return
        speed = self.sl_speed.value * 5
        thick = self.sl_thick.value
        cp = self.color_picker
        for _ in range(speed):
            if self.draw_index >= self.draw_total:
                self.drawing = False
                self.layer_count += 1
                break
            p1 = self.draw_points[self.draw_index - 1]
            p2 = self.draw_points[self.draw_index]
            col = cp.get_color(self.draw_index, self.draw_total)
            pygame.draw.line(self.canvas, col,
                             (int(p1[0]), int(p1[1])),
                             (int(p2[0]), int(p2[1])), thick)
            self.draw_index += 1

    # ── Render helpers ────────────────────────────────────────────────────────────
    def _draw_panel(self, mouse):
        panel = pygame.Surface((PANEL_W, WINDOW_H), pygame.SRCALPHA)

        # Panel background with subtle gradient feel
        panel.fill(C_PANEL)

        # Right edge border
        pygame.draw.line(panel, C_PANEL_EDGE, (PANEL_W - 1, 0), (PANEL_W - 1, WINDOW_H))

        # ── Title ──
        self._anim_tick += 1
        pulse = 0.5 + 0.5 * math.sin(self._anim_tick * 0.04)
        dot_col = lerp_color(C_ACCENT_LO, C_ACCENT, pulse) if self.drawing else C_ACCENT_LO
        pygame.draw.circle(panel, dot_col, (18, 24), 5)

        title = self.fonts["title"].render("SPIROGRAPH STUDIO", True, C_TEXT)
        panel.blit(title, (30, 15))

        self._divider(panel, 44)

        # ── Sliders ──
        for s in self.sliders:
            s.draw(panel)

        self._divider(panel, self.color_picker.y - 26)

        # ── Color picker ──
        self.color_picker.draw(panel)

        self._divider(panel, self.btn_draw.rect.y - 12)

        # ── Buttons ──
        for btn in self.buttons:
            btn.draw(panel, btn.rect.collidepoint(mouse))

        # ── Status footer ──
        pygame.draw.line(panel, C_DIVIDER, (10, WINDOW_H - 44), (PANEL_W - 10, WINDOW_H - 44))
        if self.drawing:
            pct = self.draw_index / max(self.draw_total, 1)
            bar = pygame.Rect(14, WINDOW_H - 30, PANEL_W - 28, 6)
            pygame.draw.rect(panel, C_TRACK, bar, border_radius=3)
            fill_w = int(bar.w * pct)
            if fill_w > 0:
                pygame.draw.rect(panel, C_ACCENT,
                                 pygame.Rect(bar.x, bar.y, fill_w, bar.h), border_radius=3)
            pct_lbl = self.fonts["status"].render(
                f"Drawing…  {int(pct * 100)}%", True, C_TEXT_DIM)
            panel.blit(pct_lbl, (14, WINDOW_H - 44))
        else:
            undo_avail = len(self._undo_stack)
            info = f"Layers: {self.layer_count}   Undo: {undo_avail}"
            lbl = self.fonts["status"].render(info, True, C_TEXT_DIM)
            panel.blit(lbl, (14, WINDOW_H - 38))

        self.screen.blit(panel, (0, 0))

    def _divider(self, surface, y):
        pygame.draw.line(surface, C_DIVIDER, (10, y), (PANEL_W - 10, y))

    def _draw_canvas(self):
        # Outer glow frame
        glow_rect = pygame.Rect(CANVAS_X - 6, CANVAS_Y - 6,
                                CANVAS_SIZE + 12, CANVAS_SIZE + 12)
        glow_surf = pygame.Surface((glow_rect.w, glow_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*C_ACCENT, 35), glow_surf.get_rect(), border_radius=10)
        self.screen.blit(glow_surf, glow_rect.topleft)

        # Border
        border = pygame.Rect(CANVAS_X - 2, CANVAS_Y - 2,
                             CANVAS_SIZE + 4, CANVAS_SIZE + 4)
        pygame.draw.rect(self.screen, C_PANEL_EDGE, border, 2, border_radius=6)

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
                    elif event.key == pygame.K_z and (event.mod & pygame.KMOD_META or
                                                       event.mod & pygame.KMOD_CTRL):
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
                    self.drawing = False
                    self.canvas = self._canvas_bg.copy()
                    self.layer_count = 0
                elif self.btn_save.is_clicked(event):
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    fname = os.path.join(SAVE_DIR, f"spirograph_{ts}.png")
                    pygame.image.save(self.canvas, fname)
                    pygame.display.set_caption(f"Spirograph Studio — Saved ✓")

            self._animate_step()

            # Render
            self.screen.fill(C_BG)
            self._draw_panel(mouse)
            self._draw_canvas()
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    App().run()
