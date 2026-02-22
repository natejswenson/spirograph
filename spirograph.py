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
PANEL_W  = 310
CANVAS_SIZE = 680
CANVAS_X = PANEL_W + 35
CANVAS_Y = (WINDOW_H - CANVAS_SIZE) // 2

# ── Palette ─────────────────────────────────────────────────────────────────────
C_BG          = ( 15,  12,  28)
C_PANEL       = ( 24,  20,  44)
C_CARD        = ( 32,  28,  58)
C_CARD_EDGE   = ( 55,  50,  95)
C_TEXT        = (235, 232, 255)
C_TEXT_DIM    = (140, 130, 185)
C_CANVAS_BG   = (  9,   8,  18)

# Button colors
C_DRAW   = ( 99, 102, 241)   # indigo
C_UNDO   = (217, 119,   6)   # amber
C_CLEAR  = (220,  38,  38)   # red
C_SAVE   = ( 22, 163,  74)   # green

# Slider accent colors (one per slider, makes each distinct)
SLIDER_COLORS = [
    (129, 140, 248),   # Big Circle    — lavender
    (251, 113, 133),   # Little Wheel  — pink
    ( 52, 211, 153),   # Pen Reach     — mint
    (251, 191,  36),   # Speed         — amber
    (167, 139, 250),   # Thickness     — purple
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

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def rounded_rect_surface(w, h, color, radius, alpha=255):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    r, g, b = color
    pygame.draw.rect(s, (r, g, b, alpha), s.get_rect(), border_radius=radius)
    return s

pygame.font.init()

def load_fonts():
    return {
        "title":   pygame.font.SysFont("Arial Rounded MT Bold", 15, bold=True),
        "section": pygame.font.SysFont("Arial", 12, bold=True),
        "label":   pygame.font.SysFont("Arial", 13, bold=True),
        "value":   pygame.font.SysFont("Courier New", 14, bold=True),
        "btn":     pygame.font.SysFont("Arial", 14, bold=True),
        "small":   pygame.font.SysFont("Arial", 11),
    }


# ── Card helper ──────────────────────────────────────────────────────────────────
def draw_card(surface, rect, color=C_CARD, edge=C_CARD_EDGE, radius=12):
    # Shadow
    sh = pygame.Surface((rect.w + 4, rect.h + 4), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 60), sh.get_rect(), border_radius=radius + 2)
    surface.blit(sh, (rect.x - 1, rect.y + 3))
    # Body
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    # Border
    pygame.draw.rect(surface, edge, rect, 1, border_radius=radius)


# ── Slider ───────────────────────────────────────────────────────────────────────
class Slider:
    TRACK_H  = 8
    HANDLE_R = 12
    ROW_H    = 62

    def __init__(self, x, y, w, min_val, max_val, initial,
                 emoji, label, color, fonts):
        self.x, self.y, self.w = x, y, w
        self.track = pygame.Rect(x, y + 42, w, self.TRACK_H)
        self.min_val = min_val
        self.max_val = max_val
        self._value  = float(initial)
        self.emoji   = emoji
        self.label   = label
        self.color   = color      # accent color for this slider
        self.fonts   = fonts
        self.dragging = False

    @property
    def value(self):
        return int(round(self._value))

    def _val_to_x(self, val):
        r = (val - self.min_val) / (self.max_val - self.min_val)
        return self.track.x + int(r * self.track.w)

    def _x_to_val(self, x):
        r = clamp((x - self.track.x) / self.track.w, 0.0, 1.0)
        return self.min_val + r * (self.max_val - self.min_val)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            hx = self._val_to_x(self._value)
            hy = self.track.centery
            if (math.hypot(event.pos[0] - hx, event.pos[1] - hy) <= self.HANDLE_R + 6
                    or self.track.inflate(0, 28).collidepoint(event.pos)):
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
        f = self.fonts
        # Emoji + label on left, big value on right
        em_lbl = f["label"].render(f"{self.emoji}  {self.label}", True, C_TEXT)
        surface.blit(em_lbl, (self.x, self.y + 18))

        val_str = str(self.value)
        val_surf = f["value"].render(val_str, True, self.color)
        surface.blit(val_surf, (self.track.right - val_surf.get_width(), self.y + 16))

        # Track bg
        tr = pygame.Rect(self.track.x, self.track.centery - self.TRACK_H // 2,
                         self.track.w, self.TRACK_H)
        pygame.draw.rect(surface, C_CARD_EDGE, tr, border_radius=4)

        # Filled portion with color
        hx = self._val_to_x(self._value)
        fw = hx - self.track.x
        if fw > 0:
            fr = pygame.Rect(self.track.x, self.track.centery - self.TRACK_H // 2,
                             fw, self.TRACK_H)
            pygame.draw.rect(surface, self.color, fr, border_radius=4)

        # Handle: shadow + filled circle + white inner dot
        r = self.HANDLE_R
        # Soft glow behind handle
        glow = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 55), (r * 2, r * 2), r * 2)
        surface.blit(glow, (hx - r * 2, self.track.centery - r * 2))

        pygame.draw.circle(surface, self.color,   (hx, self.track.centery), r)
        pygame.draw.circle(surface, (255, 255, 255), (hx, self.track.centery), r - 4)
        pygame.draw.circle(surface, self.color,   (hx, self.track.centery), r - 7)


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
        col = lerp_color(self.color,
                         tuple(min(255, c + 50) for c in self.color),
                         self._t)

        # Shadow
        sh = pygame.Surface((self.rect.w + 4, self.rect.h + 6), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 70), sh.get_rect(), border_radius=12)
        surface.blit(sh, (self.rect.x - 1, self.rect.y + 4))

        # Body
        pygame.draw.rect(surface, col, self.rect, border_radius=10)

        # Glossy top band
        gl = pygame.Surface((self.rect.w - 4, self.rect.h // 2 - 2), pygame.SRCALPHA)
        gl.fill((255, 255, 255, 25))
        surface.blit(gl, (self.rect.x + 2, self.rect.y + 2))

        # Border
        pygame.draw.rect(surface, (255, 255, 255, 40), self.rect, 1, border_radius=10)

        # Icon + label
        full = f"{self.icon}  {self.text}"
        lbl = self.fonts["btn"].render(full, True, (255, 255, 255))
        surface.blit(lbl, lbl.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# ── Color picker ─────────────────────────────────────────────────────────────────
class ColorPicker:
    SW = 32
    GAP = 8

    def __init__(self, x, y, fonts):
        self.x = x
        self.y = y
        self.selected = 0
        self.rainbow  = False
        self.fonts    = fonts
        self._build()

    def _build(self):
        self.rects = []
        for i in range(len(PRESET_COLORS)):
            col = i % 4
            row = i // 4
            rx = self.x + col * (self.SW + self.GAP)
            ry = self.y + row * (self.SW + self.GAP)
            self.rects.append(pygame.Rect(rx, ry, self.SW, self.SW))
        rb_y = self.y + 2 * (self.SW + self.GAP) + 10
        self.rb_rect  = pygame.Rect(self.x, rb_y, 18, 18)
        self.rb_pos   = (self.x + 26, rb_y + 1)

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

    def draw(self, surface):
        lbl = self.fonts["section"].render("🎨  Pick a Color", True, C_TEXT)
        surface.blit(lbl, (self.x, self.y - 20))

        for i, (r, col) in enumerate(zip(self.rects, PRESET_COLORS)):
            # Outer ring for selected
            if i == self.selected and not self.rainbow:
                ring = r.inflate(6, 6)
                pygame.draw.rect(surface, col, ring, border_radius=9)
            pygame.draw.rect(surface, col, r, border_radius=7)
            if i != self.selected or self.rainbow:
                # Subtle inner shadow ring
                pygame.draw.rect(surface, (0, 0, 0, 60), r, 1, border_radius=7)

        # Rainbow toggle
        rb_col = (252, 211, 40) if self.rainbow else C_CARD_EDGE
        pygame.draw.rect(surface, rb_col, self.rb_rect, border_radius=4)
        pygame.draw.rect(surface, C_TEXT_DIM, self.rb_rect, 1, border_radius=4)
        if self.rainbow:
            ck = self.fonts["small"].render("✓", True, (20, 20, 20))
            surface.blit(ck, ck.get_rect(center=self.rb_rect.center))
        lbl2 = self.fonts["label"].render("🌈  Rainbow!", True,
                                          (252, 211, 40) if self.rainbow else C_TEXT_DIM)
        surface.blit(lbl2, self.rb_pos)


# ── Spirograph math ───────────────────────────────────────────────────────────────
class Spirograph:
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


# ── Static canvas background ──────────────────────────────────────────────────────
def make_canvas_bg(size):
    surf = pygame.Surface((size, size))
    surf.fill(C_CANVAS_BG)
    # Subtle dot grid
    for gx in range(28, size, 28):
        for gy in range(28, size, 28):
            c = 25 + int(8 * math.sin(gx * 0.1) * math.cos(gy * 0.1))
            surf.set_at((gx, gy), (c, c, c + 8))
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

        self.spiro       = Spirograph()
        self.drawing     = False
        self.draw_index  = 0
        self.draw_points = []
        self.draw_total  = 0
        self.layer_count = 0
        self._undo_stack = []
        self._tick       = 0
        self._save_flash = 0   # countdown frames for save confirmation

        self.clock = pygame.time.Clock()
        self._build_ui()

    def _build_ui(self):
        f  = self.fonts
        px = 18
        # Card-based layout — each card has a top y
        card_pad = 14

        # ── Sliders card ──
        sliders_card_y = 56
        y = sliders_card_y + card_pad + 14

        sw = PANEL_W - px * 2 - 10
        slider_defs = [
            ("⭕", "Big Circle",    50, 300, 150, SLIDER_COLORS[0]),
            ("🔵", "Little Wheel",   5, 200,  80, SLIDER_COLORS[1]),
            ("✏️", "Pen Reach",      5, 250, 100, SLIDER_COLORS[2]),
            ("⚡", "Speed",          1,  20,   5, SLIDER_COLORS[3]),
            ("📏", "Line Width",     1,   8,   1, SLIDER_COLORS[4]),
        ]
        self.sliders = []
        for em, lbl, mn, mx, init, col in slider_defs:
            self.sliders.append(Slider(px, y, sw, mn, mx, init, em, lbl, col, f))
            y += Slider.ROW_H

        sliders_card_h = y - sliders_card_y + card_pad - 8
        self._sliders_card = pygame.Rect(8, sliders_card_y, PANEL_W - 8, sliders_card_h)

        # ── Color card ──
        color_card_y = sliders_card_y + sliders_card_h + 10
        self.color_picker = ColorPicker(px, color_card_y + card_pad + 20, f)
        color_card_h = 2 * (ColorPicker.SW + ColorPicker.GAP) + 50 + card_pad * 2
        self._color_card = pygame.Rect(8, color_card_y, PANEL_W - 8, color_card_h)

        # ── Buttons card ──
        btn_card_y = color_card_y + color_card_h + 10
        by = btn_card_y + card_pad
        bw, bh = PANEL_W - 8 - px * 2 + 8 - 8, 38
        self.btn_draw  = Button(px, by, bw, bh, "▶", "Draw",    C_DRAW,  f); by += bh + 6
        self.btn_undo  = Button(px, by, bw, bh, "↩", "Undo",   C_UNDO,  f); by += bh + 6
        self.btn_clear = Button(px, by, bw, bh, "✕", "Clear",  C_CLEAR, f); by += bh + 6
        self.btn_save  = Button(px, by, bw, bh, "💾", "Save",  C_SAVE,  f); by += bh + card_pad
        self._btn_card = pygame.Rect(8, btn_card_y, PANEL_W - 8, by - btn_card_y)

        self.buttons = [self.btn_draw, self.btn_undo, self.btn_clear, self.btn_save]

    # ── Undo ──────────────────────────────────────────────────────────────────────
    def _push_undo(self):
        self._undo_stack.append(self.canvas.copy())
        if len(self._undo_stack) > self.MAX_UNDO:
            self._undo_stack.pop(0)

    def _pop_undo(self):
        if self._undo_stack:
            self.drawing    = False
            self.canvas     = self._undo_stack.pop()
            self.layer_count = max(0, self.layer_count - 1)

    # ── Drawing ───────────────────────────────────────────────────────────────────
    def _clamp_r(self):
        R, r = self.sliders[0].value, self.sliders[1].value
        return min(r, R - 1) if r >= R else r

    def start_drawing(self):
        R = self.sliders[0].value
        r = self._clamp_r()
        d = self.sliders[2].value
        pts = self.spiro.compute_points(R, r, d)

        max_ext = max(max(abs(x) for x, _ in pts),
                      max(abs(y) for _, y in pts), 1)
        scale   = (CANVAS_SIZE / 2 - 28) / max_ext
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

    # ── Render ────────────────────────────────────────────────────────────────────
    def _draw_panel(self, mouse):
        self._tick += 1
        panel = pygame.Surface((PANEL_W, WINDOW_H))
        panel.fill(C_PANEL)

        # ── Title bar ──
        title_bar = pygame.Rect(0, 0, PANEL_W, 50)
        pygame.draw.rect(panel, C_CARD, title_bar)
        pygame.draw.line(panel, C_CARD_EDGE, (0, 50), (PANEL_W, 50))

        # Animated dot (pulsing when drawing)
        pulse = 0.5 + 0.5 * math.sin(self._tick * 0.07)
        dot_col = lerp_color((80, 80, 120), C_DRAW, pulse) if self.drawing else (60, 58, 100)
        pygame.draw.circle(panel, dot_col, (18, 25), 7)
        pygame.draw.circle(panel, (255, 255, 255, 120), (18, 25), 4)

        title = self.fonts["title"].render("SPIROGRAPH STUDIO", True, C_TEXT)
        panel.blit(title, (32, 16))

        # ── Slider card ──
        draw_card(panel, self._sliders_card)
        sec = self.fonts["section"].render("🎛   Adjust the Shape", True, C_TEXT_DIM)
        panel.blit(sec, (self._sliders_card.x + 12, self._sliders_card.y + 8))
        for s in self.sliders:
            s.draw(panel)

        # ── Color card ──
        draw_card(panel, self._color_card)
        self.color_picker.draw(panel)

        # ── Button card ──
        draw_card(panel, self._btn_card)
        for btn in self.buttons:
            btn.draw(panel, btn.rect.collidepoint(mouse))

        # ── Status strip ──
        strip_y = WINDOW_H - 34
        pygame.draw.line(panel, C_CARD_EDGE, (0, strip_y), (PANEL_W, strip_y))
        if self.drawing:
            pct = self.draw_index / max(self.draw_total, 1)
            bar = pygame.Rect(10, strip_y + 8, PANEL_W - 20, 6)
            pygame.draw.rect(panel, C_CARD_EDGE, bar, border_radius=3)
            if pct > 0:
                pygame.draw.rect(panel, C_DRAW,
                                 pygame.Rect(bar.x, bar.y, int(bar.w * pct), bar.h),
                                 border_radius=3)
            txt = self.fonts["small"].render(f"Drawing…  {int(pct * 100)}%",
                                             True, C_TEXT_DIM)
            panel.blit(txt, (12, strip_y + 18))
        elif self._save_flash > 0:
            self._save_flash -= 1
            txt = self.fonts["small"].render("✓  Saved to Desktop/spirograph",
                                             True, C_SAVE)
            panel.blit(txt, (12, strip_y + 10))
        else:
            undo = len(self._undo_stack)
            txt  = self.fonts["small"].render(
                f"Layers: {self.layer_count}    Undo steps: {undo}",
                True, C_TEXT_DIM)
            panel.blit(txt, (12, strip_y + 10))

        # Right edge separator line
        pygame.draw.line(panel, C_CARD_EDGE, (PANEL_W - 1, 0), (PANEL_W - 1, WINDOW_H))
        self.screen.blit(panel, (0, 0))

    def _draw_canvas(self):
        # Multi-layer glow aura
        for r, alpha in [(18, 15), (10, 30), (4, 50)]:
            aura = pygame.Surface((CANVAS_SIZE + r * 2, CANVAS_SIZE + r * 2), pygame.SRCALPHA)
            col  = C_DRAW if self.drawing else (55, 50, 95)
            pygame.draw.rect(aura, (*col, alpha), aura.get_rect(), border_radius=12 + r)
            self.screen.blit(aura, (CANVAS_X - r, CANVAS_Y - r))

        border = pygame.Rect(CANVAS_X - 2, CANVAS_Y - 2,
                             CANVAS_SIZE + 4, CANVAS_SIZE + 4)
        pygame.draw.rect(self.screen, C_CARD_EDGE, border, 2, border_radius=8)
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
                    self._save_flash = 120   # show for 2 seconds

            self._animate_step()

            self.screen.fill(C_BG)
            self._draw_panel(mouse)
            self._draw_canvas()
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    App().run()
