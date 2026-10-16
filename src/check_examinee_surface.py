from __future__ import annotations

import re
import statistics
from typing import Any

ABSOLUTE_TERMS = (
    "一定",
    "必然",
    "完全",
    "一律",
    "所有",
    "任何",
    "絕不",
    "只要",
    "唯一",
)


def _visible_length(text: str) -> int:
    return len(re.sub(r"\s+", "", str(text or "")))


def _contains_absolute_term(text: str) -> bool:
    value = str(text or "")
    return any(term in value for term in ABSOLUTE_TERMS)


def check_item_surface(item: dict[str, Any]) -> list[str]:
    """Return non-blocking warnings for answer cues visible to an examinee.

    These are heuristics, not correctness rules. They intentionally do not fail an
    item because clinically correct options can legitimately be longer or include
    strong wording. Reviewer judgment is still required.
    """
    warnings: list[str] = []
    item_id = str(item.get("item_id") or "<unknown>")
    options = item.get("options") or {}
    correct = item.get("correct_answer")
    if correct not in {"A", "B", "C", "D"}:
        return warnings
    if set(options) != {"A", "B", "C", "D"}:
        return warnings

    lengths = {letter: _visible_length(options[letter]) for letter in "ABCD"}
    correct_len = lengths[correct]
    distractor_lengths = [lengths[letter] for letter in "ABCD" if letter != correct]
    median_distractor = statistics.median(distractor_lengths)

    if (
        correct_len >= 28
        and correct_len - median_distractor >= 16
        and correct_len >= median_distractor * 1.45
    ):
        warnings.append(
            f"{item_id}: correct option is substantially longer than distractors "
            f"({correct_len} vs median {median_distractor:g}); review for length cue."
        )

    max_len = max(lengths.values())
    min_len = min(lengths.values())
    if min_len > 0 and max_len >= 36 and max_len / min_len >= 2.6:
        warnings.append(
            f"{item_id}: option lengths are highly uneven ({min_len}-{max_len}); "
            "review whether detail level reveals the answer."
        )

    distractor_absolute = sum(
        _contains_absolute_term(options[letter])
        for letter in "ABCD"
        if letter != correct
    )
    correct_absolute = _contains_absolute_term(options[correct])
    if distractor_absolute >= 2 and not correct_absolute:
        warnings.append(
            f"{item_id}: multiple distractors use absolute wording while the correct "
            "option does not; review for test-taking cue."
        )

    return warnings


def check_exam_surface(exam: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    for item in exam.get("items", []):
        warnings.extend(check_item_surface(item))
    return warnings
