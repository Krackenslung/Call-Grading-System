"""Parse rubric.md into criteria + allowed scores.

Expected shapes (from rubric.md v1.0):
    Each criterion is scored **0, 5, or 10**.
    ## C1. Greeting and Identification
"""

import re
from dataclasses import dataclass

from grader.config import RUBRIC_PATH

_SCALE_RE = re.compile(r"scored\s+\*\*([\d,\sor]+)\*\*", re.IGNORECASE)
_CRITERION_RE = re.compile(r"^##\s+(C\d+)\.\s+(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Rubric:
    text: str
    criteria: dict[str, str]  # {"C1": "Greeting and Identification", ...}
    scores: tuple[int, ...]  # (0, 5, 10)


def load_rubric() -> Rubric:
    text = RUBRIC_PATH.read_text(encoding="utf-8")

    scale = _SCALE_RE.search(text)
    if not scale:
        raise ValueError(f"{RUBRIC_PATH}: could not find the score scale ('scored **0, 5, or 10**').")
    scores = tuple(sorted(int(s) for s in re.findall(r"\d+", scale.group(1))))

    criteria = dict(_CRITERION_RE.findall(text))
    if not criteria:
        raise ValueError(f"{RUBRIC_PATH}: no criteria headings found ('## C1. Name').")

    return Rubric(text=text, criteria=criteria, scores=scores)
