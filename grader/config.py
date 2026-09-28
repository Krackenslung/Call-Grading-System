"""Single source of truth for paths and model settings.

Criteria and the score scale are NOT defined here: they are parsed from rubric.md
(see rubric.py) so that a rubric change is a one-file edit.
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RUBRIC_PATH = ROOT / "rubric.md"
LABELS_PATH = ROOT / "labels.csv"
TRANSCRIPTS_DIR = ROOT / "transcripts"
RESULTS_DIR = ROOT / "results"
RAW_DIR = RESULTS_DIR / "raw"
GRADES_PATH = RESULTS_DIR / "grades.json"
EVAL_PATH = RESULTS_DIR / "eval.md"

CALL_IDS = [f"C{i:03d}" for i in range(1, 31)]


TUNE_IDS = [f"C{i:03d}" for i in range(1, 8)]  

MODEL = "claude-opus-5-5"
EFFORT = "high"
MAX_TOKENS = 16000

MOCK = os.environ.get("MOCK", "") not in ("", "0")
