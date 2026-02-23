# Spirograph Studio

An interactive spirograph art app built with Python and Pygame. Roll a small wheel inside a large ring, adjust the pen offset, and watch intricate geometric patterns emerge — just like the classic toy.

![Spirograph Studio](https://img.shields.io/badge/Python-3.13%2B-blue) ![Pygame](https://img.shields.io/badge/Pygame-required-green)

## Features

- **Live mechanism preview** — animated outer ring, rolling inner wheel, and pen arm so you can see exactly what you're drawing before you draw it
- **Layered drawing** — draw multiple curves on top of each other to build complex compositions
- **20-level undo** — step back through your work one layer at a time
- **Rainbow mode** — full HSV spectrum gradient across any curve
- **Save to Desktop** — exports PNG to `~/Desktop/spirograph/` with a timestamp

## Quick Start

```bash
# Requires Python 3.13 (pygame has no wheel for 3.14 yet)
python3.13 -m venv .venv
source .venv/bin/activate
pip install pygame
python spirograph.py
```

## Controls

| Control | What it does |
|---------|-------------|
| **Big Circle** slider | Outer ring radius (R) |
| **Little Wheel** slider | Inner rolling wheel radius (r) |
| **Pen Reach** slider | Pen offset from wheel center (d) |
| **Speed** slider | Drawing speed (segments per frame) |
| **Line Width** slider | Stroke thickness |
| **Color swatches** | Pick a solid pen color |
| **Rainbow checkbox** | Cycle through the full color spectrum |
| **▶ Draw** | Compute and animate the current curve |
| **↩ Undo** | Remove the last drawn layer |
| **✕ Clear** | Wipe the canvas (undoable) |
| **💾 Save PNG** | Save canvas to `~/Desktop/spirograph/` |
| **Cmd/Ctrl+Z** | Keyboard undo |
| **Esc** | Quit |

## Math

Spirographs trace a [hypotrochoid](https://en.wikipedia.org/wiki/Hypotrochoid) — the path of a point attached to a smaller circle rolling inside a larger one:

```
x(t) = (R - r) * cos(t) + d * cos((R - r) * t / r)
y(t) = (R - r) * sin(t) - d * sin((R - r) * t / r)
```

The curve closes after `r / gcd(R, r)` full rotations of the inner wheel.

## Project Structure

```
spirograph/
├── spirograph.py        # Entry point
├── app.py               # Main app class, event loop
├── constants.py         # Layout geometry (window/canvas sizes)
├── theme.py             # Visual stylesheet (colors, radii, alphas)
├── drawing_engine.py    # Canvas surface, undo stack, animation state
├── preview.py           # Animated mechanism preview widget
├── renderer.py          # Frame rendering (panel + canvas)
├── spiro_math.py        # Hypotrochoid math
├── ui_layout.py         # Widget construction and card layout
├── utils.py             # Shared helpers (fonts, colors, canvas bg)
├── widgets/
│   ├── slider.py        # Slider widget
│   ├── button.py        # Button widget
│   └── color_picker.py  # Color swatch + rainbow picker
└── requirements.txt
```

## Requirements

- Python 3.13+
- pygame
