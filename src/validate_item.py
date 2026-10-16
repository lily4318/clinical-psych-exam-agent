from __future__ import annotations

import re
from typing import Iterable

REQUIRED_FIELDS = {
    "item_id",
    "form",
    "pair_id",
    "stem",
    "options",
    "correct_answer",
    "category",
    "subtopic",
    "difficulty",
    "cognitive_level",
    "rationale",
    "sources",
    "quality_status",
}
VALID_FORMS = {"甲卷", "乙卷"}
VALID_DIFFICULTY = {"基礎", "中等", "進階"}
VALID_COGNITION = {"記憶", "理解", "應用", "整合"}
VALID_CATEGORIES = set("ABCDEF")
VALID_QUALITY = {"草稿", "待複核", "已核可"}
VALID_ANSWERS = set("ABCD")
PAIR_RE = re.compile(r"^P(0[1-9]|1[0-9]|20)$")


def validate_item(item: dict, known_sources: Iterable[str] | None = None) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_FIELDS - set(item))
    if missing:
        errors.append(f"Missing required fields: {', '.join(missing)}")
        return errors

    if item["form"] not in VALID_FORMS:
        errors.append("form must be 甲卷 or 乙卷.")
    if not PAIR_RE.match(str(item["pair_id"])):
        errors.append("pair_id must be P01-P20.")
    if item["category"] not in VALID_CATEGORIES:
        errors.append("category must be A-F.")
    if item["difficulty"] not in VALID_DIFFICULTY:
        errors.append("difficulty must be 基礎/中等/進階.")
    if item["cognitive_level"] not in VALID_COGNITION:
        errors.append("cognitive_level must be 記憶/理解/應用/整合.")
    if item["quality_status"] not in VALID_QUALITY:
        errors.append("quality_status must be 草稿/待複核/已核可.")

    stem = str(item["stem"]).strip()
    if not stem:
        errors.append("stem cannot be empty.")

    options = item["options"]
    if not isinstance(options, dict) or set(options) != VALID_ANSWERS:
        errors.append("options must contain exactly A, B, C and D.")
    else:
        normalized = [str(options[k]).strip() for k in "ABCD"]
        if any(not value for value in normalized):
            errors.append("All four options must be non-empty.")
        if len(set(normalized)) != 4:
            errors.append("All four option texts must be unique.")

    answer = item["correct_answer"]
    if answer not in VALID_ANSWERS:
        errors.append("correct_answer must be A, B, C or D.")

    rationale = item["rationale"]
    if not isinstance(rationale, dict) or not {"correct", "A", "B", "C", "D"}.issubset(rationale):
        errors.append("rationale must contain correct and A-D explanations.")

    sources = item["sources"]
    if not isinstance(sources, list) or not sources:
        errors.append("sources must contain at least one source ID.")
    elif known_sources is not None:
        known = set(known_sources)
        missing_sources = sorted(source for source in sources if source not in known)
        if missing_sources:
            errors.append(f"Unknown source IDs: {', '.join(missing_sources)}")

    return errors
