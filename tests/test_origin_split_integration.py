import pytest
from src.ml_evaluation import chronological_diagnostic_split


def test_split_summary_discloses_missing_origin_provenance():
    _, _, meta = chronological_diagnostic_split([{"item_id": "111-Q1", "year": "111"}, {"item_id": "115-Q1", "year": "115"}])
    assert meta["origin_group_audit"]["status"] == "unverified_missing_provenance"
    assert meta["is_blind_test"] is False


def test_split_rejects_shared_origins_even_with_unique_item_ids():
    with pytest.raises(ValueError, match="Origin group leaked"):
        chronological_diagnostic_split([
            {"item_id": "111-Q1", "year": "111", "origin_group_id": "shared"},
            {"item_id": "115-Q2", "year": "115", "origin_group_id": "shared"},
        ])


def test_cli_direct_script_remains_usable():
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(root / "src" / "ml_evaluation.py"), "--help"],
        cwd=root, capture_output=True, text=True, check=False, timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert "--history" in result.stdout
