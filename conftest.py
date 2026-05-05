"""
Root conftest — configure sys.path for all tests.

ml-pipeline tests import directly from data/, models/, utils/ (relative to ml-pipeline/).
backend tests import from app (relative to backend/).
"""
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
ML_PIPELINE_DIR = os.path.join(ROOT, 'ml-pipeline')
BACKEND_DIR = os.path.join(ROOT, 'backend')

# Add ml-pipeline dir so tests can do: from data.xxx import ...
if ML_PIPELINE_DIR not in sys.path:
    sys.path.insert(0, ML_PIPELINE_DIR)

# Add root so ml-pipeline/config.py is importable as config
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Add backend dir so tests can do: from app import app
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
