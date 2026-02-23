# Spirograph Studio

An interactive spirograph art app built with Python. Roll a small wheel inside a large ring, adjust the pen offset, and watch intricate geometric patterns emerge — just like the classic toy.

Runs in two modes: a **Pygame desktop app** and a **terminal TUI** (via Textual + Kitty Graphics Protocol).

## Screenshot

![Spirograph Studio TUI](assets/tui.png)

## Features

- **Animated drawing** — curves animate onto the canvas segment by segment
- **Layered drawing** — draw multiple curves on top of each other to build complex compositions
- **20-level undo** — step back through your work one layer at a time
- **Rainbow mode** — full HSV spectrum gradient across any curve
- **Save to Desktop** — exports PNG to `~/Desktop/spirograph/` with a timestamp

## Quick Start

### Terminal TUI (Ghostty / Kitty terminal recommended)

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install pygame pillow textual textual-image
./spirograph_tui.py
```

### Pygame Desktop App

```bash
source .venv/bin/activate
python spirograph.py
```

> **Note:** Requires Python 3.13 — pygame has no wheel for 3.14+.

## TUI Controls

| Control | What it does |
|---------|-------------|
| **Big Circle** slider | Outer ring radius (R) |
| **Little Wheel** slider | Inner rolling wheel radius (r) |
| **Pen Reach** slider | Pen offset from wheel center (d) |
| **Speed** slider | Drawing speed (segments per frame) |
| **Thickness** slider | Stroke width |
| **Color swatches** | Pick a solid pen color (click or ← →) |
| **Rainbow mode** | Press `r` to cycle through the full spectrum |
| **DRAW** button | Compute and animate the current curve (or press `d`) |
| **UNDO** button | Remove the last drawn layer |
| **CLEAR** button | Wipe the canvas (undoable) |
| **SAVE** button | Save canvas PNG to `~/Desktop/spirograph/` |
| `Ctrl+Z` | Keyboard undo |
| `Esc` / `q` | Quit |

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
├── spirograph.py        # Pygame entry point
├── spirograph_tui.py    # TUI entry point
├── app.py               # Pygame app class, event loop
├── constants.py         # Layout geometry (window/canvas sizes)
├── theme.py             # Visual stylesheet (colors, radii, alphas)
├── drawing_engine.py    # Pygame canvas, undo stack, animation state
├── spiro_math.py        # Hypotrochoid math (shared by both apps)
├── tui/
│   ├── app.py           # Textual app, layout, tick loop
│   ├── drawing_engine.py# PIL canvas, undo stack, animation state
│   ├── theme.tcss       # Textual CSS
│   └── widgets/
│       ├── canvas.py    # Canvas display (textual-image / TGP)
│       ├── slider.py    # Draggable slider widget
│       └── color_picker.py # Color swatch + rainbow picker
└── requirements.txt
```

## Requirements

- Python 3.13+
- `pygame` — desktop app
- `pillow`, `textual`, `textual-image` — terminal TUI
