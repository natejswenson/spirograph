# CLAUDE.md — Spirograph Studio

Instructions and context for Claude Code when working on this project.

## Key Rules

1. **Commit often** — after every discrete task or fix, create a git commit with a clear message explaining *why*, not just *what*.
2. **Update this file** — after implementing changes, update the relevant section below with anything worth preserving: architectural decisions, gotchas, patterns, file roles.
3. **Use `.venv/bin/python`** to run the app (`python3.13 -m venv .venv` — pygame has no wheel for Python 3.14+).
4. **No magic numbers** — all visual constants belong in `theme.py`; layout/geometry constants belong in `constants.py`.

## Architecture

### File Roles

| File | Responsibility |
|------|---------------|
| `spirograph.py` | Entry point only — `App().run()` |
| `app.py` | App class: init, event handling, main loop |
| `constants.py` | Layout geometry: window/canvas sizes, save dir |
| `theme.py` | Visual stylesheet: all colors, radii, alphas, font sizes |
| `drawing_engine.py` | Canvas surface, undo stack, animated drawing state |
| `preview.py` | Animated mechanism preview widget (local surface approach) |
| `renderer.py` | Stateless frame rendering: `draw_panel()`, `draw_canvas()` |
| `spiro_math.py` | `SpiroMath`: hypotrochoid math, period calculation |
| `ui_layout.py` | `build_ui()`: constructs all widgets and card rects |
| `utils.py` | Shared helpers: `load_fonts`, `draw_card`, `make_canvas_bg`, `lerp_color`, `gcd` |
| `widgets/slider.py` | `Slider` widget |
| `widgets/button.py` | `Button` widget |
| `widgets/color_picker.py` | `ColorPicker` widget (swatches + rainbow mode) |

### Key Decisions

- **Preview centering fix**: `PreviewWidget.draw()` renders everything into a local `sz×sz` Surface with `center=(sz//2, sz//2)`, then blits once. Never mix panel-absolute and widget-relative coordinates.
- **Canvas persistence**: `DrawingEngine.canvas` is an offscreen Surface. `step()` draws segments incrementally each frame; the surface persists so partial curves remain visible.
- **Undo**: list of Surface copies (max 20). `push_undo()` before every canvas-modifying operation.
- **r clamped to R-1**: `App.r()` returns `min(slider.value, R-1)` to prevent degenerate math.
- **Period**: `loops = r // gcd(R, r)` gives the number of inner wheel rotations to close the curve.
- **CANVAS_MARGIN = 28**: padding used in `drawing_engine.py` when scaling points to the canvas.
- **SLIDER_ROW_H = 44**: vertical pitch between sliders, defined in `theme.py`, used by `Slider.ROW_H` and `ui_layout.py`.

### Layout Math (panel height budget)

Window height: 720px. Panel contents must fit in ~688px (32px footer margin).

- Title bar: 44px
- Preview card: `PREVIEW_SIZE + 22 = 177px` + 6px gap
- Sliders card: `5 × 44 + 32 = 252px` + 6px gap
- Color card: `26 + 40 = 66px` + 6px gap
- Button card: `33 + 6 + 33 + 6 = 78px`

If layout overflows, first check `PREVIEW_SIZE`, `SLIDER_ROW_H`, and button heights.

## Commit Message Format

```
<type>: <short description>

<optional body explaining motivation or context>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`

## Running

```bash
source .venv/bin/activate
python spirograph.py
```
