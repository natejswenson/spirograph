import pygame
import math
import colorsys
from datetime import datetime

# ── Constants ──────────────────────────────────────────────────────────────────
WINDOW_W, WINDOW_H = 900, 650
PANEL_W = 280
CANVAS_SIZE = 620
CANVAS_X = PANEL_W
CANVAS_Y = (WINDOW_H - CANVAS_SIZE) // 2

BG_COLOR = (18, 18, 28)
PANEL_BG = (28, 28, 42)
CANVAS_BG = (10, 10, 18)
TEXT_COLOR = (220, 220, 235)
ACCENT = (100, 110, 200)
HANDLE_COLOR = (180, 190, 255)
TRACK_COLOR = (60, 65, 100)
SWATCH_BORDER = (80, 85, 130)

PRESET_COLORS = [
    (255, 255, 255),   # white
    (255,  70,  70),   # red
    (255, 160,  40),   # orange
    (255, 230,  50),   # yellow
    ( 60, 220,  90),   # green
    ( 40, 220, 220),   # cyan
    ( 60, 100, 255),   # blue
    (220,  60, 220),   # magenta
]

pygame.font.init()


def gcd(a, b):
    a, b = int(round(a)), int(round(b))
    while b:
        a, b = b, a % b
    return a


def lcm(a, b):
    g = gcd(a, b)
    return (a // g) * b if g else 0


# ── Slider ─────────────────────────────────────────────────────────────────────
class Slider:
    HEIGHT = 18
    HANDLE_R = 9

    def __init__(self, x, y, w, min_val, max_val, initial, label, integer=True):
        self.rect = pygame.Rect(x, y, w, self.HEIGHT)
        self.min_val = min_val
        self.max_val = max_val
        self._value = initial
        self.label = label
        self.integer = integer
        self.dragging = False
        self.font = pygame.font.SysFont("monospace", 13)
        self.label_font = pygame.font.SysFont("sans", 13)

    @property
    def value(self):
        return int(round(self._value)) if self.integer else self._value

    def _val_to_x(self, val):
        ratio = (val - self.min_val) / (self.max_val - self.min_val)
        return self.rect.x + int(ratio * self.rect.w)

    def _x_to_val(self, x):
        ratio = (x - self.rect.x) / self.rect.w
        ratio = max(0.0, min(1.0, ratio))
        return self.min_val + ratio * (self.max_val - self.min_val)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            hx = self._val_to_x(self._value)
            hr = pygame.Rect(hx - self.HANDLE_R, self.rect.centery - self.HANDLE_R,
                             self.HANDLE_R * 2, self.HANDLE_R * 2)
            if hr.collidepoint(event.pos) or self.rect.inflate(0, 20).collidepoint(event.pos):
                self.dragging = True
                self._value = self._x_to_val(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._value = self._x_to_val(event.pos[0])
                return True
        return False

    def draw(self, surface):
        # Label
        lbl = self.label_font.render(self.label, True, TEXT_COLOR)
        surface.blit(lbl, (self.rect.x, self.rect.y - 17))

        # Track
        track_rect = pygame.Rect(self.rect.x, self.rect.centery - 3, self.rect.w, 6)
        pygame.draw.rect(surface, TRACK_COLOR, track_rect, border_radius=3)

        # Filled portion
        hx = self._val_to_x(self._value)
        filled = pygame.Rect(self.rect.x, self.rect.centery - 3, hx - self.rect.x, 6)
        if filled.w > 0:
            pygame.draw.rect(surface, ACCENT, filled, border_radius=3)

        # Handle
        pygame.draw.circle(surface, HANDLE_COLOR, (hx, self.rect.centery), self.HANDLE_R)
        pygame.draw.circle(surface, ACCENT, (hx, self.rect.centery), self.HANDLE_R, 2)

        # Value text
        val_str = str(self.value) if self.integer else f"{self._value:.1f}"
        val_surf = self.font.render(val_str, True, HANDLE_COLOR)
        surface.blit(val_surf, (self.rect.right + 8, self.rect.centery - val_surf.get_height() // 2))


# ── Button ─────────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, x, y, w, h, text, color=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.base_color = color or ACCENT
        self.font = pygame.font.SysFont("sans", 14, bold=True)

    def draw(self, surface, hovered=False):
        col = tuple(min(255, c + 30) for c in self.base_color) if hovered else self.base_color
        pygame.draw.rect(surface, col, self.rect, border_radius=6)
        pygame.draw.rect(surface, HANDLE_COLOR, self.rect, 1, border_radius=6)
        lbl = self.font.render(self.text, True, (255, 255, 255))
        surface.blit(lbl, lbl.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


# ── ColorPicker ────────────────────────────────────────────────────────────────
class ColorPicker:
    SWATCH_SIZE = 24
    SWATCH_GAP = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.selected = 0        # index into PRESET_COLORS
        self.rainbow = False
        self.font = pygame.font.SysFont("sans", 13)
        self._build_rects()

    def _build_rects(self):
        self.swatch_rects = []
        row_w = (self.SWATCH_SIZE + self.SWATCH_GAP) * 4 - self.SWATCH_GAP
        for i, _ in enumerate(PRESET_COLORS):
            col = i % 4
            row = i // 4
            rx = self.x + col * (self.SWATCH_SIZE + self.SWATCH_GAP)
            ry = self.y + row * (self.SWATCH_SIZE + self.SWATCH_GAP)
            self.swatch_rects.append(pygame.Rect(rx, ry, self.SWATCH_SIZE, self.SWATCH_SIZE))

        # Rainbow checkbox
        rainbow_y = self.y + 2 * (self.SWATCH_SIZE + self.SWATCH_GAP) + 6
        self.rainbow_rect = pygame.Rect(self.x, rainbow_y, 14, 14)
        self.rainbow_label_pos = (self.x + 20, rainbow_y)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self.swatch_rects):
                if r.collidepoint(event.pos):
                    self.selected = i
                    self.rainbow = False
                    return True
            if self.rainbow_rect.collidepoint(event.pos):
                self.rainbow = not self.rainbow
                return True
        return False

    def get_color(self, t, total):
        if self.rainbow:
            hue = (t / max(total, 1)) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            return (int(r * 255), int(g * 255), int(b * 255))
        return PRESET_COLORS[self.selected]

    def draw(self, surface):
        lbl = self.font.render("Color:", True, TEXT_COLOR)
        surface.blit(lbl, (self.x, self.y - 18))

        for i, (r, color) in enumerate(zip(self.swatch_rects, PRESET_COLORS)):
            pygame.draw.rect(surface, color, r, border_radius=4)
            if i == self.selected and not self.rainbow:
                pygame.draw.rect(surface, (255, 255, 255), r, 2, border_radius=4)
            else:
                pygame.draw.rect(surface, SWATCH_BORDER, r, 1, border_radius=4)

        # Rainbow checkbox
        cb_color = (255, 200, 50) if self.rainbow else TRACK_COLOR
        pygame.draw.rect(surface, cb_color, self.rainbow_rect, border_radius=2)
        pygame.draw.rect(surface, HANDLE_COLOR, self.rainbow_rect, 1, border_radius=2)
        if self.rainbow:
            check = self.font.render("✓", True, (30, 30, 30))
            surface.blit(check, check.get_rect(center=self.rainbow_rect.center))
        lbl2 = self.font.render("Rainbow", True, TEXT_COLOR)
        surface.blit(lbl2, self.rainbow_label_pos)


# ── Spirograph ─────────────────────────────────────────────────────────────────
class Spirograph:
    def __init__(self):
        self.points = []

    def get_period(self, R, r):
        """Return t-steps needed for full curve."""
        ri = max(1, int(round(r)))
        Ri = max(1, int(round(R)))
        g = gcd(Ri, ri)
        loops = ri // g
        return loops

    def compute_points(self, R, r, d, steps=4000):
        """Compute hypotrochoid points centered at (0, 0)."""
        loops = self.get_period(R, r)
        total_t = 2 * math.pi * loops
        pts = []
        for i in range(steps + 1):
            t = total_t * i / steps
            x = (R - r) * math.cos(t) + d * math.cos((R - r) * t / max(r, 0.001))
            y = (R - r) * math.sin(t) - d * math.sin((R - r) * t / max(r, 0.001))
            pts.append((x, y))
        self.points = pts
        return pts


# ── App ────────────────────────────────────────────────────────────────────────
class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("Spirograph")

        self.canvas = pygame.Surface((CANVAS_SIZE, CANVAS_SIZE))
        self.canvas.fill(CANVAS_BG)

        self.spiro = Spirograph()
        self.drawing = False
        self.draw_index = 0
        self.draw_points = []
        self.draw_total = 0

        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont("sans", 18, bold=True)
        self.small_font = pygame.font.SysFont("sans", 12)

        self._build_ui()

    def _build_ui(self):
        px = 20  # panel content x
        y = 50

        # Sliders
        sw = PANEL_W - px - 40  # slider width leaving room for value label
        self.slider_R = Slider(px, y, sw, 50, 300, 150, "R  (outer radius)")
        y += 50
        self.slider_r = Slider(px, y, sw, 5, 200, 80, "r  (inner radius)")
        y += 50
        self.slider_d = Slider(px, y, sw, 5, 250, 100, "d  (pen offset)")
        y += 50
        self.slider_speed = Slider(px, y, sw, 1, 20, 5, "Speed")
        y += 50
        self.slider_thick = Slider(px, y, sw, 1, 8, 1, "Thickness")
        y += 55

        # Color picker
        self.color_picker = ColorPicker(px, y + 18)
        y += 90

        # Buttons
        bw, bh = PANEL_W - px * 2, 34
        self.btn_draw = Button(px, y, bw, bh, "Draw")
        y += bh + 8
        self.btn_clear = Button(px, y, bw, bh, "Clear", color=(60, 80, 100))
        y += bh + 8
        self.btn_save = Button(px, y, bw, bh, "Save PNG", color=(60, 110, 70))

        self.sliders = [self.slider_R, self.slider_r, self.slider_d, self.slider_speed, self.slider_thick]
        self.buttons = [self.btn_draw, self.btn_clear, self.btn_save]

        self.hovered_btn = None

    def _clamp_r(self):
        """Ensure r < R (hypotrochoid requires inner < outer)."""
        R = self.slider_R.value
        r = self.slider_r.value
        if r >= R:
            # Don't mutate slider directly; just clamp at compute time
            return min(r, R - 1)
        return r

    def start_drawing(self):
        R = self.slider_R.value
        r = self._clamp_r()
        d = self.slider_d.value
        pts = self.spiro.compute_points(R, r, d, steps=6000)

        # Scale to canvas
        max_extent = max(abs(x) for x, _ in pts + [(1, 0)])
        max_extent = max(max_extent, max(abs(y) for _, y in pts + [(0, 1)]))
        scale = (CANVAS_SIZE / 2 - 20) / max_extent if max_extent > 0 else 1.0

        cx, cy = CANVAS_SIZE // 2, CANVAS_SIZE // 2
        self.draw_points = [(cx + x * scale, cy + y * scale) for x, y in pts]
        self.draw_total = len(self.draw_points)
        self.draw_index = 1
        self.drawing = True
        # Canvas is NOT cleared here — curves layer on top of each other.
        # Use the Clear button to wipe the canvas.

    def _draw_panel(self):
        panel = pygame.Surface((PANEL_W, WINDOW_H))
        panel.fill(PANEL_BG)

        # Title
        title = self.title_font.render("SPIROGRAPH", True, HANDLE_COLOR)
        panel.blit(title, title.get_rect(centerx=PANEL_W // 2, y=14))

        # Divider
        pygame.draw.line(panel, TRACK_COLOR, (10, 38), (PANEL_W - 10, 38))

        for s in self.sliders:
            s.draw(panel)

        # Divider before color
        pygame.draw.line(panel, TRACK_COLOR, (10, self.color_picker.y - 25),
                         (PANEL_W - 10, self.color_picker.y - 25))
        self.color_picker.draw(panel)

        # Divider before buttons
        pygame.draw.line(panel, TRACK_COLOR, (10, self.btn_draw.rect.y - 10),
                         (PANEL_W - 10, self.btn_draw.rect.y - 10))

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            # Translate mouse pos to panel-local coords
            local_pos = (mouse_pos[0], mouse_pos[1])
            hovered = btn.rect.collidepoint(local_pos)
            btn.draw(panel, hovered)

        # Progress bar when drawing
        if self.drawing and self.draw_total > 0:
            progress = self.draw_index / self.draw_total
            bar_y = WINDOW_H - 20
            pygame.draw.rect(panel, TRACK_COLOR, (10, bar_y, PANEL_W - 20, 8), border_radius=4)
            pygame.draw.rect(panel, ACCENT,
                             (10, bar_y, int((PANEL_W - 20) * progress), 8), border_radius=4)
            pct = self.small_font.render(f"{int(progress * 100)}%", True, TEXT_COLOR)
            panel.blit(pct, (PANEL_W // 2 - pct.get_width() // 2, bar_y - 16))

        self.screen.blit(panel, (0, 0))

    def _draw_canvas_frame(self):
        # Canvas border
        frame = pygame.Rect(CANVAS_X - 2, CANVAS_Y - 2, CANVAS_SIZE + 4, CANVAS_SIZE + 4)
        pygame.draw.rect(self.screen, TRACK_COLOR, frame, 2, border_radius=4)
        self.screen.blit(self.canvas, (CANVAS_X, CANVAS_Y))

    def _animate_step(self):
        if not self.drawing:
            return
        speed = self.slider_speed.value * 4  # segments per frame
        thick = self.slider_thick.value
        cp = self.color_picker
        for _ in range(speed):
            if self.draw_index >= self.draw_total:
                self.drawing = False
                break
            p1 = self.draw_points[self.draw_index - 1]
            p2 = self.draw_points[self.draw_index]
            color = cp.get_color(self.draw_index, self.draw_total)
            pygame.draw.line(self.canvas, color,
                             (int(p1[0]), int(p1[1])),
                             (int(p2[0]), int(p2[1])), thick)
            self.draw_index += 1

    def run(self):
        running = True
        while running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

                # Panel widgets receive events at panel-local coords
                handled = False
                for s in self.sliders:
                    if s.handle_event(event):
                        handled = True
                if not handled:
                    self.color_picker.handle_event(event)

                if self.btn_draw.is_clicked(event):
                    self.start_drawing()
                elif self.btn_clear.is_clicked(event):
                    self.drawing = False
                    self.canvas.fill(CANVAS_BG)
                elif self.btn_save.is_clicked(event):
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    fname = f"spirograph_{ts}.png"
                    pygame.image.save(self.canvas, fname)
                    pygame.display.set_caption(f"Spirograph — Saved: {fname}")

            self._animate_step()

            # Render
            self.screen.fill(BG_COLOR)
            self._draw_panel()
            self._draw_canvas_frame()
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    App().run()
