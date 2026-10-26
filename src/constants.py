"""
src/constants.py
Central location for all file paths and configuration constants.
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

DATA_CSV = os.path.join(DATA_DIR, "data.csv")
MODEL_JSON = os.path.join(DATA_DIR, "model.json")
HISTORY_JSON = os.path.join(DATA_DIR, "history.json")
BLACKLIST_JSON = os.path.join(DATA_DIR, "blacklist.json")
