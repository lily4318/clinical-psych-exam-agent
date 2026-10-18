from __future__ import annotations

import pytest

from src.ml_evaluation import chronological_diagnostic_split, evaluate_expert_adjudications


def test_partition_is_by_year_not_random_items() -> None:
    items = [
        {"item_id": f"{year}-Q01", "year": str(year)}
        for year in (110, 111, 112, 113, 114, 115)
    ]
    training, diagnostic, meta = chronological_diagnostic_split(items)
    assert meta["train_years"] == [111, 112, 113, 114]
    assert meta["diagnostic_test_year"] == 115
    assert {item["item_id"] for item in training} == {
        "111-Q01", "112-Q01", "113-Q01", "114-Q01"
    }
    assert [item["item_id"] for item in diagnostic] == ["115-Q01"]
    assert meta["is_blind_test"] is False


def test_partition_does_not_accept_duplicate_ids() -> None:
    with pytest.raises(ValueError, match="unique"):
        chronological_diagnostic_split([
            {"item_id": "same", "year": "114"},
            {"item_id": "same", "year": "115"},
        ])


def test_quality_requires_all_five_criteria() -> None:
    base = {
        "factually_correct": "true",
        "single_best_answer": "true",
        "rationale_supported": "true",
        "blueprint_aligned": "true",
        "no_critical_error": "true",
    }
    result = evaluate_expert_adjudications([
        {"item_id": "A-01", **base},
        {"item_id": "A-02", **base, "single_best_answer": "false"},
    ])
    assert result["accepted"] == 1
    assert result["total"] == 2
    assert result["accuracy"] == 0.5
    assert result["reached_target"] is False


def test_missing_review_labels_must_not_count_as_passes() -> None:
    with pytest.raises(ValueError, match="missing"):
        evaluate_expert_adjudications([{"item_id": "A-01", "factually_correct": True}])
