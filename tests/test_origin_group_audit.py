from __future__ import annotations

import pytest
from src.origin_group_audit import audit_origin_groups


def row(item_id: str, group: str | None = None) -> dict[str, str]:
    record = {"item_id": item_id}
    if group is not None:
        record["origin_group_id"] = group
    return record


def test_missing_column_is_not_declared_leak_free() -> None:
    result = audit_origin_groups([row("111-Q1")], [row("115-Q1")])
    assert result["status"] == "unverified_missing_provenance"
    assert result["missing_origin_group_count"] == 2
    assert result["is_blind_test"] is False


def test_shared_origin_across_years_detected() -> None:
    result = audit_origin_groups([row("111-Q1", "source-1")], [row("115-Q1", "source-1")])
    assert result["status"] == "leak_detected"
    assert result["shared_origin_groups"] == ["source-1"]


def test_complete_disjoint_origins_have_no_known_overlap() -> None:
    result = audit_origin_groups([row("111-Q1", "source-1")], [row("115-Q1", "source-2")])
    assert result["status"] == "no_known_overlap"
    assert result["missing_origin_group_count"] == 0
    assert result["is_blind_test"] is False


def test_partial_or_whitespace_metadata_is_unverified() -> None:
    result = audit_origin_groups(
        [row("111-Q1", "source-1"), row("112-Q1", "  ")],
        [row("115-Q1", "source-2")],
    )
    assert result["status"] == "unverified_missing_provenance"
    assert result["missing_origin_group_count"] == 1


def test_overlap_takes_priority_over_missing_metadata() -> None:
    result = audit_origin_groups(
        [row("111-Q1", "source-1"), row("112-Q1")],
        [row("115-Q1", "source-1")],
    )
    assert result["status"] == "leak_detected"
    assert result["missing_origin_group_count"] == 1


def test_invalid_inputs_fail_closed() -> None:
    with pytest.raises(ValueError, match="nonblank"):
        audit_origin_groups([row("a")], [row("b")], field="")
    with pytest.raises(ValueError, match="nonempty"):
        audit_origin_groups([], [row("b")])
