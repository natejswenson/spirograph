#!/usr/bin/env python3.13
"""Entry point for Spirograph Studio TUI (Textual + Kitty/TGP)."""
import sys
import os

# Ensure root package is on the path so tui/ can import spiro_math, theme, constants
sys.path.insert(0, os.path.dirname(__file__))

from tui.app import SpirographTUIApp

if __name__ == "__main__":
    SpirographTUIApp().run()
