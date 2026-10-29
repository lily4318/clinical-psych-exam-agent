"""Candidate new-domain planning only; never generates items or changes formal releases."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .load_exam_history import load_recent_historical_index

ROOT = Path(__file__).resolve().parents[1]
CHILD_BLUEPRINT = ROOT / "config" / "domain_blueprints" / "child_adolescent.yaml"

DIFFICULTY = {"basic": "基礎", "medium": "中等", "advanced": "進階"}
COGNITION = {
    "memory": "記憶",
    "understanding": "理解",
    "application": "應用",
    "integration": "整合",
}


def _nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def validate_domain_blueprint(data: dict[str, Any]) -> None:
    """Check that a new-domain blueprint is internally sound and source-linked."""
    if not isinstance(data, dict) or data.get("domain_id") != "child_adolescent":
        raise ValueError("Expected a child_adolescent domain blueprint.")
    if data.get("status") != "provisional_pending_child_historical_analysis":
        raise ValueError("Child blueprint must remain explicitly provisional.")
    history = data.get("historical_evidence")
    if not isinstance(history, dict) or history.get("distribution_validated_against_child_exam_items") is not False:
        raise ValueError("Do not claim verified child exam frequencies without a source audit.")
    forms = data.get("forms")
    if not isinstance(forms, dict) or forms.get("names") != ["甲卷", "乙卷"]:
        raise ValueError("Blueprint must specify parallel 甲卷/乙卷.")
    baseline = forms.get("baseline_items_per_form")
    if not _nonnegative_int(baseline) or baseline < 1:
        raise ValueError("baseline_items_per_form must be a positive integer.")

    sources = data.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("A source catalog is required.")
    for source_id, source in sources.items():
        if not isinstance(source, dict) or not isinstance(source.get("url"), str):
            raise ValueError(f"Invalid source entry: {source_id}")
        if not source["url"].startswith("https://"):
            raise ValueError(f"Source needs HTTPS URL: {source_id}")
        if not str(source.get("title", "")).strip():
            raise ValueError(f"Source needs title: {source_id}")

    categories = data.get("categories")
    if not isinstance(categories, dict) or not categories:
        raise ValueError("New-domain categories are required.")
    for key, category in categories.items():
        if not isinstance(category, dict):
            raise ValueError(f"Invalid category {key}.")
        items = category.get("baseline_items")
        if not _nonnegative_int(items) or items < 1:
            raise ValueError(f"Invalid baseline count in category {key}.")
        goals = category.get("focus_areas")
        if not isinstance(goals, list) or not goals or not all(
            isinstance(goal, str) and goal.strip() for goal in goals
        ):
            raise ValueError(f"Missing focus_areas in category {key}.")
        references = category.get("source_ids")
        if not isinstance(references, list) or not references or any(
            source_id not in sources or sources[source_id].get("kind") != "clinical_guideline"
            for source_id in references
        ):
            raise ValueError(f"Missing authoritative clinical sources in category {key}.")
    if sum(category["baseline_items"] for category in categories.values()) != baseline:
        raise ValueError("Category targets do not sum to baseline items.")

    targets = data.get("targets")
    if not isinstance(targets, dict):
        raise ValueError("Missing difficulty/cognition targets.")
    for name, expected in (("difficulty", DIFFICULTY), ("cognition", COGNITION)):
        counts = targets.get(name)
        if not isinstance(counts, dict) or list(counts) != list(expected):
            raise ValueError(f"Invalid {name} labels.")
        if not all(_nonnegative_int(value) for value in counts.values()):
            raise ValueError(f"Invalid {name} counts.")
        if sum(counts.values()) != baseline:
            raise ValueError(f"{name} counts do not sum to baseline.")


def load_domain_blueprint(path: str | Path = CHILD_BLUEPRINT) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    validate_domain_blueprint(data)
    return data


def _largest_remainder(counts: dict[str, int], total: int) -> dict[str, int]:
    if isinstance(total, bool) or not isinstance(total, int) or total < 1:
        raise ValueError("Requested item count must be a positive integer.")
    denominator = sum(counts.values())
    if denominator < 1:
        raise ValueError("Cannot scale zero-weight distribution.")
    allocated = {key: value * total // denominator for key, value in counts.items()}
    remaining = total - sum(allocated.values())
    ranking = sorted(
        counts,
        key=lambda key: (-((counts[key] * total) % denominator), list(counts).index(key)),
    )
    for key in ranking[:remaining]:
        allocated[key] += 1
    return allocated


def _interleave(counts: dict[str, int]) -> list[str]:
    remaining = counts.copy()
    sequence: list[str] = []
    while any(remaining.values()):
        for key in remaining:
            if remaining[key]:
                sequence.append(key)
                remaining[key] -= 1
    return sequence


def build_child_pair_specs(
    items_per_form: int = 20,
    *,
    blueprint: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Plan paired exam slots, NOT generated or clinically verified questions.

    Counts for a non-20 form are reallocated across the child-domain topics,
    difficulty and cognitive targets rather than truncating the first N slots.
    """
    data = load_domain_blueprint() if blueprint is None else blueprint
    validate_domain_blueprint(data)

    cats = data["categories"]
    categories = _interleave(_largest_remainder(
        {key: value["baseline_items"] for key, value in cats.items()},
        items_per_form,
    ))
    difficulty = _interleave(_largest_remainder(data["targets"]["difficulty"], items_per_form))
    cognition = _interleave(_largest_remainder(data["targets"]["cognition"], items_per_form))
    seen: dict[str, int] = {key: 0 for key in cats}
    pairs: list[dict[str, Any]] = []
    for number, (category_id, diff, cog) in enumerate(
        zip(categories, difficulty, cognition), start=1
    ):
        cat = cats[category_id]
        goal = cat["focus_areas"][seen[category_id] % len(cat["focus_areas"])]
        seen[category_id] += 1
        pair_id = f"P{number:02d}"
        pairs.append({
            "pair_id": pair_id,
            "form_a_item": f"A-{pair_id}",
            "form_b_item": f"B-{pair_id}",
            "category": category_id,
            "core_topic": goal,
            "difficulty": DIFFICULTY[diff],
            "cognitive_level": COGNITION[cog],
            "source_ids": list(cat["source_ids"]),
            "source_status": "candidate_requires_item_level_verification",
            "equivalence_note": "同考點、同難度／認知層次；實際題幹與答案須另行獨立檢核",
        })
    return pairs


def available_exam_years(
    index_path: str | Path | None = None,
    *,
    count: int = 5,
) -> list[int]:
    """Dynamic year window ONLY; historical index is NOT child-domain calibrated."""
    history = load_recent_historical_index(index_path, count=count)
    return sorted({int(row["year"]) for row in history})
