"""Evaluation helpers for leak-aware Agent optimisation.

This module does NOT fine-tune an LLM. It creates a reproducible historical
diagnostic split and scores *independently adjudicated* new exam items.

The publicly indexed historical exam questions are NOT a blind holdout.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
CRITERIA = (
    "factually_correct",
    "single_best_answer",
    "rationale_supported",
    "blueprint_aligned",
    "no_critical_error",
)


def _read_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def chronological_diagnostic_split(
    rows: Iterable[dict[str, Any]], *, recent_years: int = 5
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Use older years for development; newest year for diagnostic evaluation.

    WARNING: this public dataset was already used in prior item development
    and cannot be counted as a fresh, independent final test.
    """
    if recent_years < 2:
        raise ValueError("recent_years must be at least 2.")
    data = list(rows)
    if not data:
        raise ValueError("No historical items were supplied.")
    years: set[int] = set()
    ids: set[str] = set()
    for row in data:
        year = int(str(row.get("year", "")).strip())
        item_id = str(row.get("item_id", "")).strip()
        if not item_id or item_id in ids:
            raise ValueError("Item IDs must be nonblank and unique.")
        ids.add(item_id)
        years.add(year)
    selected = sorted(years)[-recent_years:]
    if len(selected) < 2:
        raise ValueError("Need at least two distinct years.")
    holdout_year, train_years = selected[-1], selected[:-1]
    train = [row for row in data if int(str(row["year"])) in train_years]
    test = [row for row in data if int(str(row["year"])) == holdout_year]
    if not train or not test:
        raise ValueError("Train and diagnostic test data must be non-empty.")
    if {r["item_id"] for r in train} & {r["item_id"] for r in test}:
        raise ValueError("Item ID leaked between partitions.")
    summary = {
        "train_years": train_years,
        "diagnostic_test_year": holdout_year,
        "train_count": len(train),
        "diagnostic_test_count": len(test),
        "is_blind_test": False,
        "warning": "Historical data is public and previously referenced; this is NOT independent final evaluation.",
    }
    return train, test, summary


def _as_boolean(value: Any, field: str) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "pass", "通過"}:
        return True
    if normalized in {"false", "0", "no", "fail", "未通過"}:
        return False
    raise ValueError(f"Invalid or missing expert label in {field}: {value!r}")


def evaluate_expert_adjudications(
    records: Iterable[dict[str, Any]],
    *,
    target: float = 0.90,
) -> dict[str, Any]:
    """Score labeled NEW questions. All criteria must pass for an item to pass.

    Caller must enforce provenance, expert independence, and data isolation.
    """
    rows = list(records)
    if not rows:
        raise ValueError("No independently adjudicated questions were supplied.")
    if not 0 < target <= 1:
        raise ValueError("target must be in (0,1].")
    ids: set[str] = set()
    accepted = 0
    for row in rows:
        item_id = str(row.get("item_id", "")).strip()
        if not item_id or item_id in ids:
            raise ValueError("Expert review item IDs must be unique and nonblank.")
        ids.add(item_id)
        if all(_as_boolean(row.get(field), field) for field in CRITERIA):
            accepted += 1
    total = len(rows)
    return {
        "accepted": accepted,
        "total": total,
        "accuracy": accepted / total,
        "target": target,
        "reached_target": accepted / total >= target,
        "interpretation": "Expert-adjudicated item validity; NOT model answer prediction accuracy.",
        "independence_verification_required": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Report dataset split or score expert-rated new items.")
    parser.add_argument("--history", type=Path, default=ROOT / "data" / "historical_exam_index.csv")
    parser.add_argument("--expert-review", type=Path, help="CSV with item_id and all required expert criteria.")
    args = parser.parse_args()
    _, _, summary = chronological_diagnostic_split(_read_csv(args.history))
    output: dict[str, Any] = {"historical_partition": summary, "blind_test_status": "not_available"}
    if args.expert_review:
        output["expert_review"] = evaluate_expert_adjudications(_read_csv(args.expert_review))
        output["blind_test_status"] = "provenance_requires_independent_verification"
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
