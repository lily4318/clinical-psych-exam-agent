from __future__ import annotations

import pytest

from src.ml_evaluation import evaluate_expert_adjudications


def _records(count: int = 100) -> list[dict[str, object]]:
    return [
        {
            "item_id": f"new-{i:03d}",
            "factually_correct": True,
            "single_best_answer": True,
            "rationale_supported": True,
            "blueprint_aligned": True,
            "no_critical_error": True,
        }
        for i in range(count)
    ]


def test_independence_attestation_is_required() -> None:
    result = evaluate_expert_adjudications(_records())
    assert result["accuracy"] == 1.0
    assert result["reached_target"] is False


def test_minimum_100_new_items_required() -> None:
    result = evaluate_expert_adjudications(_records(99), independence_verified=True)
    assert result["sample_size_sufficient"] is False
    assert result["reached_target"] is False


def test_ninety_percent_without_critical_error_meets_numeric_gate() -> None:
    rows = _records()
    for row in rows[:10]:
        row["blueprint_aligned"] = False
    result = evaluate_expert_adjudications(rows, independence_verified=True)
    assert result["accepted"] == 90
    assert result["critical_failures"] == 0
    assert result["reached_target"] is True


def test_critical_error_vetoes_high_accuracy() -> None:
    rows = _records()
    rows[0]["no_critical_error"] = False
    result = evaluate_expert_adjudications(rows, independence_verified=True)
    assert result["accepted"] == 99
    assert result["critical_failures"] == 1
    assert result["reached_target"] is False


def test_wilson_interval_is_bounded_and_contains_estimate() -> None:
    rows = _records()
    for row in rows[:10]:
        row["factually_correct"] = False
    result = evaluate_expert_adjudications(rows, independence_verified=True)
    ci = result["confidence_interval_95"]
    assert 0 <= ci["lower"] <= result["accuracy"] <= ci["upper"] <= 1
    assert ci["lower"] < 0.9


def test_invalid_attestation_or_incomplete_labels_rejected() -> None:
    with pytest.raises(ValueError, match="boolean"):
        evaluate_expert_adjudications(_records(), independence_verified="yes")
    rows = _records()
    rows[0].pop("rationale_supported")
    with pytest.raises(ValueError, match="missing"):
        evaluate_expert_adjudications(rows)
