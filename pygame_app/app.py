import os
import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        self.cards        = ui["cards"]
        self.buttons      = ui["buttons"]
        self.btn_draw, self.btn_undo, self.btn_clear, self.btn_save = self.buttons

        self.save_flash = 0
        self.tick       = 0
        self.clock      = pygame.time.Clock()

    # ── Slider value accessors ─────────────────────────────────────────────────
    def R(self): return self.sliders[0].value
    def r(self): return min(self.sliders[1].value, self.R() - 1)
    def d(self): return self.sliders[2].value

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

            if self.btn_draw.is_clicked(event):
                self.engine.start(self.R(), self.r(), self.d())
            elif self.btn_undo.is_clicked(event):
                self.engine.pop_undo()
            elif self.btn_clear.is_clicked(event):
                self.engine.clear()
            elif self.btn_save.is_clicked(event):
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
            self.tick += 1
            mouse = pygame.mouse.get_pos()

            running = self._handle_events()

            self.engine.step(
                self.sliders[3].value * 5,
                self.sliders[4].value,
                self.color_picker,
            )

            draw_canvas(self.screen, self)
            draw_panel(self.screen, self, mouse, self.tick)
            pygame.display.flip()

        pygame.quit()
