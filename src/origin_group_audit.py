"""Audit shared-origin groups across chronological diagnostic partitions.

An origin-group ID identifies questions derived from the same source question.
Missing provenance is *unknown*, never evidence of no leakage. This audit
cannot prove semantic independence or model-pretraining non-exposure.
"""
from __future__ import annotations

from typing import Any, Iterable


def audit_origin_groups(
    development: Iterable[dict[str, Any]],
    diagnostic: Iterable[dict[str, Any]],
    *,
    field: str = "origin_group_id",
) -> dict[str, Any]:
    """Report known shared-origin groups and incomplete provenance coverage.

    A clean result means only no overlap among supplied group IDs.
    """
    if not isinstance(field, str) or not field.strip():
        raise ValueError("origin group field must be a nonblank string")
    development_rows, diagnostic_rows = list(development), list(diagnostic)
    if not development_rows or not diagnostic_rows:
        raise ValueError("both partitions must be nonempty")

    def collect(rows: list[dict[str, Any]]) -> tuple[set[str], int]:
        groups: set[str] = set()
        missing = 0
        for row in rows:
            value = row.get(field)
            group = str(value).strip() if value is not None else ""
            if not group:
                missing += 1
            else:
                groups.add(group)
        return groups, missing

    dev_groups, dev_missing = collect(development_rows)
    diag_groups, diag_missing = collect(diagnostic_rows)
    overlaps = sorted(dev_groups & diag_groups)
    missing_total = dev_missing + diag_missing
    status = (
        "leak_detected" if overlaps
        else "unverified_missing_provenance" if missing_total
        else "no_known_overlap"
    )
    return {
        "status": status,
        "field": field,
        "development_count": len(development_rows),
        "diagnostic_count": len(diagnostic_rows),
        "missing_origin_group_count": missing_total,
        "shared_origin_groups": overlaps,
        "is_blind_test": False,
        "note": "Known-ID audit only; semantic/model-training contamination remains unverified.",
    }
