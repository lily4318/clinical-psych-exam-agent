from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BLUEPRINT = ROOT / "config" / "blueprint.yaml"
DEFAULT_PARALLEL_BLUEPRINT = ROOT / "config" / "parallel_form_blueprint.csv"
DEFAULT_SOURCE_REQUIREMENTS = ROOT / "config" / "pair_source_requirements.yaml"

CATEGORY_CODES = tuple("ABCDEF")


def load_blueprint(path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path) if path else DEFAULT_BLUEPRINT
    with target.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise ValueError("blueprint.yaml must contain a mapping.")

    forms = data.get("forms", {})
    if forms.get("items_per_form") != 20:
        raise ValueError("This Agent currently requires exactly 20 items per form.")

    categories = data.get("categories", {})
    if tuple(categories.keys()) != CATEGORY_CODES:
        raise ValueError("Blueprint categories must be A-F in order.")

    category_total = sum(int(categories[code]["items_per_form"]) for code in CATEGORY_CODES)
    if category_total != forms["items_per_form"]:
        raise ValueError(
            f"Category item counts sum to {category_total}, expected {forms['items_per_form']}."
        )

    difficulty_total = sum(int(v) for v in data["form_level_targets"]["difficulty"].values())
    cognition_total = sum(int(v) for v in data["form_level_targets"]["cognition"].values())
    if difficulty_total != forms["items_per_form"]:
        raise ValueError("Form-level difficulty targets do not sum to items_per_form.")
    if cognition_total != forms["items_per_form"]:
        raise ValueError("Form-level cognition targets do not sum to items_per_form.")

    return data


def load_parallel_blueprint(path: str | Path | None = None) -> list[dict[str, str]]:
    target = Path(path) if path else DEFAULT_PARALLEL_BLUEPRINT
    with target.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    expected_columns = {
        "pair_id",
        "form_a_item",
        "form_b_item",
        "category",
        "core_topic",
        "difficulty",
        "cognitive_level",
        "equivalence_note",
    }
    if not rows:
        raise ValueError("Parallel blueprint is empty.")
    if set(rows[0]) != expected_columns:
        raise ValueError("Parallel blueprint columns do not match the expected schema.")

    pair_ids = [row["pair_id"] for row in rows]
    if len(rows) != 20 or len(set(pair_ids)) != 20:
        raise ValueError("Parallel blueprint must contain 20 unique pair IDs.")
    if pair_ids != [f"P{i:02d}" for i in range(1, 21)]:
        raise ValueError("Parallel pair IDs must be ordered P01-P20.")

    for row in rows:
        if row["category"] not in CATEGORY_CODES:
            raise ValueError(f"Invalid category in {row['pair_id']}: {row['category']}")
        if row["difficulty"] not in {"基礎", "中等", "進階"}:
            raise ValueError(f"Invalid difficulty in {row['pair_id']}.")
        if row["cognitive_level"] not in {"記憶", "理解", "應用", "整合"}:
            raise ValueError(f"Invalid cognitive level in {row['pair_id']}.")

    return rows


def load_pair_source_requirements(
    path: str | Path | None = None,
) -> dict[str, dict[str, list[str]]]:
    target = Path(path) if path else DEFAULT_SOURCE_REQUIREMENTS
    with target.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict) or not isinstance(data.get("pairs"), dict):
        raise ValueError("pair_source_requirements.yaml must contain a pairs mapping.")

    expected_pairs = [f"P{i:02d}" for i in range(1, 21)]
    if list(data["pairs"].keys()) != expected_pairs:
        raise ValueError("Source requirements must define P01-P20 in order.")

    result: dict[str, dict[str, list[str]]] = {}
    for pair_id, rules in data["pairs"].items():
        if not isinstance(rules, dict):
            raise ValueError(f"{pair_id} source requirements must be a mapping.")
        require_all = list(rules.get("require_all") or [])
        require_any = list(rules.get("require_any") or [])
        if not require_all and not require_any:
            raise ValueError(f"{pair_id} must define require_all or require_any.")
        if len(set(require_all + require_any)) != len(require_all + require_any):
            raise ValueError(f"{pair_id} contains duplicate source requirements.")
        result[pair_id] = {
            "require_all": require_all,
            "require_any": require_any,
        }
    return result
