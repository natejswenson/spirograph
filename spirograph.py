import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pygame_app"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import App

if __name__ == "__main__":
    App().run()
