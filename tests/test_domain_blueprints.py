"""Regression tests for a *candidate* child/adolescent domain plan, not AI output."""

from collections import Counter
from copy import deepcopy

import pytest

from src.domain_blueprints import (
    available_exam_years,
    build_child_pair_specs,
    load_domain_blueprint,
    validate_domain_blueprint,
)


def test_child_blueprint_is_distinct_and_explicitly_provisional():
    data = load_domain_blueprint()
    assert data["domain_id"] == "child_adolescent"
    assert data["scope"]["examinee_level"].startswith("臨床心理師國考程度")
    assert data["historical_evidence"]["child_specific_items_indexed"] is False
    assert data["historical_evidence"]["distribution_validated_against_child_exam_items"] is False
    assert sum(c["baseline_items"] for c in data["categories"].values()) == 20
    assert all(
        "物質濫用" not in c["name"] and "成癮" not in c["name"]
        for c in data["categories"].values()
    )


def test_source_catalog_covers_all_child_categories():
    data = load_domain_blueprint()
    assert "MOEX-115-CLINICAL-II" in data["sources"]
    for category in data["categories"].values():
        assert category["source_ids"]
        assert all(
            data["sources"][sid]["kind"] == "clinical_guideline"
            for sid in category["source_ids"]
        )


@pytest.mark.parametrize("count", [1, 7, 10, 20, 37])
def test_pair_plan_reallocates_category_difficulty_and_cognition(count):
    data = load_domain_blueprint()
    snapshot = deepcopy(data)
    pairs = build_child_pair_specs(count, blueprint=data)
    assert len(pairs) == count
    assert [p["pair_id"] for p in pairs] == [f"P{i:02d}" for i in range(1, count + 1)]
    assert len({p["form_a_item"] for p in pairs}) == count
    assert len({p["form_b_item"] for p in pairs}) == count
    assert all(p["form_a_item"] != p["form_b_item"] for p in pairs)
    assert sum(Counter(p["category"] for p in pairs).values()) == count
    assert sum(Counter(p["difficulty"] for p in pairs).values()) == count
    assert sum(Counter(p["cognitive_level"] for p in pairs).values()) == count
    assert all(p["source_status"] == "candidate_requires_item_level_verification" for p in pairs)
    assert all(p["source_ids"] for p in pairs)
    assert data == snapshot  # planning must not overwrite the baseline


def test_twenty_question_allocation_uses_child_baseline():
    data = load_domain_blueprint()
    pairs = build_child_pair_specs(20)
    categories = Counter(p["category"] for p in pairs)
    assert categories == {
        code: cat["baseline_items"] for code, cat in data["categories"].items()
    }
    assert Counter(p["difficulty"] for p in pairs) == {
        "基礎": 3, "中等": 11, "進階": 6
    }
    assert Counter(p["cognitive_level"] for p in pairs) == {
        "記憶": 2, "理解": 7, "應用": 8, "整合": 3
    }


@pytest.mark.parametrize("count", [0, -1, 1.5, True, "10"])
def test_nonpositive_or_nonnumeric_requested_item_count_rejected(count):
    with pytest.raises(ValueError, match="positive integer"):
        build_child_pair_specs(count)


def test_child_plan_rejects_missing_clinical_source():
    data = load_domain_blueprint()
    data["categories"]["ADHD"]["source_ids"] = ["NOT-A-REAL-SOURCE"]
    with pytest.raises(ValueError, match="Missing authoritative clinical sources"):
        validate_domain_blueprint(data)


def test_child_plan_rejects_unbalanced_baseline():
    data = load_domain_blueprint()
    data["categories"]["ADHD"]["baseline_items"] += 1
    with pytest.raises(ValueError, match="do not sum"):
        validate_domain_blueprint(data)


def test_child_plan_rejects_falsely_verified_distribution():
    data = load_domain_blueprint()
    data["historical_evidence"]["distribution_validated_against_child_exam_items"] = True
    with pytest.raises(ValueError, match="verified child exam frequencies"):
        validate_domain_blueprint(data)


def test_historical_window_is_dynamic_not_hardcoded(tmp_path):
    headings = (
        "item_id,year,source_item,category,subtopic,"
        "assessment_focus,difficulty,cognitive_level\n"
    )
    rows = "".join(
        f"X-{year},{year},Q01,testing,testing,testing,中等,理解\n"
        for year in range(111, 117)
    )
    index = tmp_path / "synthetic_history.csv"
    index.write_text(headings + rows, encoding="utf-8")
    assert available_exam_years(index) == [112, 113, 114, 115, 116]
    assert available_exam_years(index, count=2) == [115, 116]


def test_actual_index_years_are_only_window_metadata():
    assert available_exam_years() == [111, 112, 113, 114, 115]
    assert load_domain_blueprint()["historical_evidence"]["child_specific_items_indexed"] is False
