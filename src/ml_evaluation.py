"""Evaluation helpers for leak-aware Agent optimisation.

This module does NOT fine-tune an LLM. It creates a reproducible historical
diagnostic split and scores *independently adjudicated* new exam items.

The publicly indexed historical exam questions are NOT a blind holdout.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any, Iterable

if __package__:
    from .origin_group_audit import audit_origin_groups
else:
    from origin_group_audit import audit_origin_groups

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
    origin_audit = audit_origin_groups(train, test)
    if origin_audit["shared_origin_groups"]:
        raise ValueError(
            "Origin group leaked between partitions: "
            + ", ".join(origin_audit["shared_origin_groups"])
        )
    summary = {
        "train_years": train_years,
        "diagnostic_test_year": holdout_year,
        "train_count": len(train),
        "diagnostic_test_count": len(test),
        "is_blind_test": False,
        "origin_group_audit": origin_audit,
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


def _wilson_interval(successes: int, total: int) -> dict[str, float]:
    """Two-sided 95% Wilson score interval for a binomial proportion."""
    z = 1.959963984540054
    p = successes / total
    z2 = z * z
    denominator = 1 + z2 / total
    center = (p + z2 / (2 * total)) / denominator
    half_width = z * math.sqrt(p * (1 - p) / total + z2 / (4 * total * total)) / denominator
    return {"lower": max(0.0, center - half_width), "upper": min(1.0, center + half_width)}


def evaluate_expert_adjudications(
    records: Iterable[dict[str, Any]],
    *,
    target: float = 0.90,
    minimum_items: int = 100,
    independence_verified: bool = False,
) -> dict[str, Any]:
    """Score labeled NEW questions. All criteria must pass for an item to pass.

    independence_verified is an external attestation, NOT a technical proof.
    The default prevents scoring a local CSV as a verified blind test.
    """
    rows = list(records)
    if not rows:
        raise ValueError("No independently adjudicated questions were supplied.")
    if not 0 < target <= 1:
        raise ValueError("target must be in (0,1].")
    if minimum_items < 1:
        raise ValueError("minimum_items must be positive.")
    if not isinstance(independence_verified, bool):
        raise ValueError("independence_verified must be a boolean attestation.")
    ids: set[str] = set()
    accepted = 0
    critical_failures = 0
    for row in rows:
        item_id = str(row.get("item_id", "")).strip()
        if not item_id or item_id in ids:
            raise ValueError("Expert review item IDs must be unique and nonblank.")
        ids.add(item_id)
        checks = [_as_boolean(row.get(field), field) for field in CRITERIA]
        if not checks[-1]:
            critical_failures += 1
        if all(checks):
            accepted += 1
    total = len(rows)
    rate = accepted / total
    numeric_target_met = rate >= target
    sample_size_sufficient = total >= minimum_items
    passed_all_gates = (
        numeric_target_met and sample_size_sufficient
        and critical_failures == 0 and independence_verified
    )
    return {
        "accepted": accepted,
        "total": total,
        "accuracy": rate,
        "confidence_interval_95": _wilson_interval(accepted, total),
        "target": target,
        "minimum_items": minimum_items,
        "sample_size_sufficient": sample_size_sufficient,
        "critical_failures": critical_failures,
        "numeric_target_met": numeric_target_met,
        "reached_target": passed_all_gates,
        "interpretation": "Expert-adjudicated item validity; NOT model answer prediction accuracy.",
        "independence_verification_required": not independence_verified,
        "independence_attestation_is_external": True,
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
