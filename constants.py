# constants.py
# Centralised file paths and configuration values for PhishGuard.

import os

# ---------- Base paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
REPORT_DIR = os.path.join(BASE_DIR, "report")

# ---------- Data files ----------
SAMPLE_CSV = os.path.join(DATA_DIR, "sample_emails.csv")
FULL_CSV = os.path.join(DATA_DIR, "data.csv")
MODEL_JSON = os.path.join(DATA_DIR, "model.json")
HISTORY_JSON = os.path.join(DATA_DIR, "history.json")
BLACKLIST_JSON = os.path.join(DATA_DIR, "blacklist.json")

# ---------- CSV columns ----------
REQUIRED_COLUMNS = ["sender", "receiver", "date", "subject", "body", "label", "urls"]

# ---------- Detector settings ----------
RULE_WEIGHT = 0.4
BAYES_WEIGHT = 0.6
THRESHOLD_SAFE = 35        # score <= 35  → SAFE
THRESHOLD_PHISHING = 65    # score >= 65  → PHISHING
                           # between      → SUSPICIOUS

# ---------- Model settings ----------
TRAIN_RATIO = 0.80
RANDOM_SEED = 42
