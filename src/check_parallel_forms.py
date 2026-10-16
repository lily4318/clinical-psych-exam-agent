from __future__ import annotations

from collections import Counter
from typing import Any

from .validate_item import validate_item


def _longest_run(values: list[str]) -> int:
    longest = current = 0
    previous = None
    for value in values:
        if value == previous:
            current += 1
        else:
            current = 1
            previous = value
        longest = max(longest, current)
    return longest


def _counts(items: list[dict], key: str) -> Counter:
    return Counter(item.get(key) for item in items)


def check_form(
    exam: dict[str, Any],
    blueprint: dict[str, Any],
    known_sources: set[str] | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    items = exam.get("items", [])
    expected_n = int(blueprint["forms"]["items_per_form"])

    if exam.get("form") not in blueprint["forms"]["names"]:
        errors.append("Exam form is not defined in blueprint.")
    if len(items) != expected_n:
        errors.append(f"Expected {expected_n} items, found {len(items)}.")

    item_ids = [item.get("item_id") for item in items]
    if len(set(item_ids)) != len(item_ids):
        errors.append("Duplicate item_id values found.")

    for item in items:
        for error in validate_item(item, known_sources):
            errors.append(f"{item.get('item_id', '<unknown>')}: {error}")

    expected_category = {
        code: int(config["items_per_form"])
        for code, config in blueprint["categories"].items()
    }
    actual_category = _counts(items, "category")
    if {k: actual_category.get(k, 0) for k in expected_category} != expected_category:
        errors.append(
            f"Category distribution mismatch: actual={dict(actual_category)}, "
            f"expected={expected_category}."
        )

    diff_map = {"basic": "基礎", "medium": "中等", "advanced": "進階"}
    expected_difficulty = {
        diff_map[key]: int(value)
        for key, value in blueprint["form_level_targets"]["difficulty"].items()
    }
    actual_difficulty = _counts(items, "difficulty")
    if {k: actual_difficulty.get(k, 0) for k in expected_difficulty} != expected_difficulty:
        errors.append(
            f"Difficulty distribution mismatch: actual={dict(actual_difficulty)}, "
            f"expected={expected_difficulty}."
        )

    cognition_map = {
        "memory": "記憶",
        "understanding": "理解",
        "application": "應用",
        "integration": "整合",
    }
    expected_cognition = {
        cognition_map[key]: int(value)
        for key, value in blueprint["form_level_targets"]["cognition"].items()
    }
    actual_cognition = _counts(items, "cognitive_level")
    if {k: actual_cognition.get(k, 0) for k in expected_cognition} != expected_cognition:
        errors.append(
            f"Cognition distribution mismatch: actual={dict(actual_cognition)}, "
            f"expected={expected_cognition}."
        )

    answers = [item.get("correct_answer") for item in items if item.get("correct_answer")]
    answer_counts = Counter(answers)
    if answers:
        counts = [answer_counts.get(letter, 0) for letter in "ABCD"]
        if max(counts) - min(counts) > 2:
            warnings.append(f"Answer positions are imbalanced: {dict(answer_counts)}.")
        if _longest_run(answers) >= 4:
            warnings.append("Four or more consecutive items share the same answer position.")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "category": dict(actual_category),
            "difficulty": dict(actual_difficulty),
            "cognition": dict(actual_cognition),
            "answers": dict(answer_counts),
        },
    }


def check_parallel_forms(
    form_a: dict[str, Any],
    form_b: dict[str, Any],
    blueprint: dict[str, Any],
    pairs: list[dict[str, str]],
    known_sources: set[str] | None = None,
) -> dict[str, Any]:
    report_a = check_form(form_a, blueprint, known_sources)
    report_b = check_form(form_b, blueprint, known_sources)
    errors = [f"甲卷: {e}" for e in report_a["errors"]]
    errors += [f"乙卷: {e}" for e in report_b["errors"]]
    warnings = [f"甲卷: {w}" for w in report_a["warnings"]]
    warnings += [f"乙卷: {w}" for w in report_b["warnings"]]

    by_pair_a = {item.get("pair_id"): item for item in form_a.get("items", [])}
    by_pair_b = {item.get("pair_id"): item for item in form_b.get("items", [])}

    for spec in pairs:
        pair_id = spec["pair_id"]
        a = by_pair_a.get(pair_id)
        b = by_pair_b.get(pair_id)
        if not a or not b:
            errors.append(f"{pair_id}: missing paired item in one or both forms.")
            continue

        for item, label in ((a, "甲卷"), (b, "乙卷")):
            if item.get("category") != spec["category"]:
                errors.append(f"{pair_id} {label}: category does not match pair blueprint.")
            if item.get("difficulty") != spec["difficulty"]:
                errors.append(f"{pair_id} {label}: difficulty does not match pair blueprint.")
            if item.get("cognitive_level") != spec["cognitive_level"]:
                errors.append(f"{pair_id} {label}: cognitive level does not match pair blueprint.")

        normalized_a = " ".join(str(a.get("stem", "")).split()).casefold()
        normalized_b = " ".join(str(b.get("stem", "")).split()).casefold()
        if normalized_a and normalized_a == normalized_b:
            errors.append(f"{pair_id}: paired stems are identical; use different scenarios.")

    expected_pairs = {row["pair_id"] for row in pairs}
    if set(by_pair_a) != expected_pairs:
        errors.append("甲卷 pair_id set does not exactly match P01-P20 blueprint.")
    if set(by_pair_b) != expected_pairs:
        errors.append("乙卷 pair_id set does not exactly match P01-P20 blueprint.")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "forms": {"甲卷": report_a, "乙卷": report_b},
    }


def main() -> None:
    import argparse
    import json
    from pathlib import Path

    from .load_blueprint import load_blueprint, load_parallel_blueprint
    from .load_exam_history import (
        known_source_ids,
        load_historical_index,
        load_official_sources,
    )

    parser = argparse.ArgumentParser(description="Validate two generated parallel-form JSON files.")
    parser.add_argument("form_a", type=Path)
    parser.add_argument("form_b", type=Path)
    args = parser.parse_args()

    form_a = json.loads(args.form_a.read_text(encoding="utf-8"))
    form_b = json.loads(args.form_b.read_text(encoding="utf-8"))
    report = check_parallel_forms(
        form_a,
        form_b,
        load_blueprint(),
        load_parallel_blueprint(),
        known_source_ids(load_historical_index(), load_official_sources()),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
