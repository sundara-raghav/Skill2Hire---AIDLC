"""WSGI entry point."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, load_models

load_models()

if __name__ == '__main__':
    app.run()
