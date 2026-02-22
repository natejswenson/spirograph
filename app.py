import os
import pygame
from datetime import datetime

from constants import WINDOW_W, WINDOW_H, SAVE_DIR
from utils import load_fonts
from drawing_engine import DrawingEngine
from ui_layout import build_ui
from renderer import draw_panel, draw_canvas


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("Spirograph Studio")

        self.fonts  = load_fonts()
        self.engine = DrawingEngine()

        ui = build_ui(self.fonts)
        self.preview      = ui["preview"]
        self.sliders      = ui["sliders"]
        self.color_picker = ui["color_picker"]
        self.buttons      = ui["buttons"]
        self.cards        = ui["cards"]
        self._btn_draw    = ui["btn_draw"]
        self._btn_undo    = ui["btn_undo"]
        self._btn_clear   = ui["btn_clear"]
        self._btn_save    = ui["btn_save"]

        self.save_flash = 0
        self._tick      = 0
        self.clock      = pygame.time.Clock()

    # ── Slider value accessors ─────────────────────────────────────────────────
    def _R(self): return self.sliders[0].value
    def _r(self): return min(self.sliders[1].value, self._R() - 1)
    def _d(self): return self.sliders[2].value

    # ── Event handling ─────────────────────────────────────────────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_z and (event.mod & pygame.KMOD_META
                                                or event.mod & pygame.KMOD_CTRL):
                    self.engine.pop_undo()

            handled = any(s.handle_event(event) for s in self.sliders)
            if not handled:
                self.color_picker.handle_event(event)

            if self._btn_draw.is_clicked(event):
                self.engine.start(self._R(), self._r(), self._d())
            elif self._btn_undo.is_clicked(event):
                self.engine.pop_undo()
            elif self._btn_clear.is_clicked(event):
                self.engine.clear()
            elif self._btn_save.is_clicked(event):
                self._save()

        return True

    def _save(self):
        fname = os.path.join(SAVE_DIR,
                             f"spirograph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        pygame.image.save(self.engine.canvas, fname)
        self.save_flash = 120

    # ── Main loop ──────────────────────────────────────────────────────────────
    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            self._tick += 1
            mouse = pygame.mouse.get_pos()

            running = self._handle_events()

            speed = self.sliders[3].value * 5
            thick = self.sliders[4].value
            self.engine.step(speed, thick, self.color_picker)

            draw_canvas(self.screen, self)
            draw_panel(self.screen, self, mouse, self._tick)
            pygame.display.flip()

        pygame.quit()
