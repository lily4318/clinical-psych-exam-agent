"""No-network tests for standalone child evidence preparation."""

import json
from pathlib import Path

import pytest

from src import prepare_child_evidence as module


def _fake_fetch(calls):
    def fetch(catalog, source_ids):
        calls.append(set(source_ids))
        return {
            sid: {
                "url": catalog[sid]["url"],
                "passage": "Synthetic transport test passage; not clinical guidance. " * 4,
                "retrieved_at": "2026-10-26T00:00:00Z",
                "verification_status": "retrieved_excerpt_not_semantically_verified",
            }
            for sid in source_ids
        }
    return fetch


@pytest.mark.parametrize("count,expected", [
    (1, {"NICE-NG87"}),
    (20, {"NICE-NG87", "NICE-CG128", "NICE-NG11", "NICE-NG134", "NICE-NG225"}),
])
def test_prepare_sources_without_model_or_word(monkeypatch, tmp_path, count, expected):
    calls = []
    monkeypatch.setattr(module, "fetch_official_guidance_evidence", _fake_fetch(calls))
    path = tmp_path / "evidence" / "child.json"
    assert module.prepare_child_evidence(path, items_per_form=count) == path
    assert calls == [expected]
    assert set(json.loads(path.read_text(encoding="utf-8"))) == expected
    assert not list(tmp_path.rglob("*.docx"))
    assert not list(path.parent.glob(".child-evidence-stage-*"))


def test_existing_output_fails_before_network_without_overwrite(monkeypatch, tmp_path):
    path = tmp_path / "evidence.json"
    path.write_text("original", encoding="utf-8")
    monkeypatch.setattr(
        module, "fetch_official_guidance_evidence",
        lambda *args: pytest.fail("network must not be used"),
    )
    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        module.prepare_child_evidence(path)
    assert path.read_text(encoding="utf-8") == "original"


def test_network_failure_does_not_publish_partial_evidence(monkeypatch, tmp_path):
    def blocked(*args):
        raise RuntimeError("HTTP 403: official source unavailable")
    monkeypatch.setattr(module, "fetch_official_guidance_evidence", blocked)
    path = tmp_path / "evidence.json"
    with pytest.raises(RuntimeError, match="HTTP 403"):
        module.prepare_child_evidence(path)
    assert not path.exists()


def test_missing_source_preflight_blocks_publication(monkeypatch, tmp_path):
    def incomplete(catalog, source_ids):
        result = _fake_fetch([])(catalog, source_ids)
        result.pop(next(iter(source_ids)))
        return result
    monkeypatch.setattr(module, "fetch_official_guidance_evidence", incomplete)
    path = tmp_path / "evidence.json"
    with pytest.raises(ValueError, match="missing clinical source passage"):
        module.prepare_child_evidence(path, items_per_form=1)
    assert not path.exists()


@pytest.mark.parametrize("count", [0, -1, True, 1.5])
def test_invalid_item_count_never_fetches(monkeypatch, tmp_path, count):
    monkeypatch.setattr(
        module, "fetch_official_guidance_evidence",
        lambda *args: pytest.fail("network must not be used"),
    )
    with pytest.raises(ValueError, match="positive integer"):
        module.prepare_child_evidence(tmp_path / "evidence.json", items_per_form=count)


def test_exclusive_publish_failure_leaves_no_partial_file(monkeypatch, tmp_path):
    monkeypatch.setattr(module, "fetch_official_guidance_evidence", _fake_fetch([]))
    def no_hardlink(*args):
        raise OSError("hard links unsupported")
    monkeypatch.setattr(module.os, "link", no_hardlink)
    path = tmp_path / "evidence.json"
    with pytest.raises(OSError, match="hard links unsupported"):
        module.prepare_child_evidence(path, items_per_form=1)
    assert not path.exists()
    assert not list(tmp_path.glob(".child-evidence-stage-*"))
