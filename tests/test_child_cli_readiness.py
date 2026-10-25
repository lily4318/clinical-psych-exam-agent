"""No-network CLI tests: local model preflight never generates a clinical item."""

import json
import sys

import pytest

from src import child_exam_pipeline


class _ReadyLocalModel:
    calls = []

    def __init__(self, *, model=None):
        self.model = model or "test-local"
        self.calls.append(("init", self.model))

    def check_ready(self):
        self.calls.append(("ready", self.model))
        return self.model


def test_check_local_model_needs_no_evidence_and_no_generation(monkeypatch, capsys):
    _ReadyLocalModel.calls = []
    monkeypatch.setattr(child_exam_pipeline, "OllamaLocalJsonCallback", _ReadyLocalModel)
    monkeypatch.setattr(
        child_exam_pipeline, "generate_child_parallel_docx",
        lambda *args, **kwargs: pytest.fail("preflight must not generate"),
    )
    monkeypatch.setattr(
        child_exam_pipeline, "fetch_official_guidance_evidence",
        lambda *args, **kwargs: pytest.fail("preflight must not fetch sources"),
    )
    monkeypatch.setattr(
        sys, "argv", ["exam", "--check-local-model", "--model", "test-local"]
    )
    child_exam_pipeline.main()
    assert _ReadyLocalModel.calls == [("init", "test-local"), ("ready", "test-local")]
    assert "no inference or download" in capsys.readouterr().out


def test_generation_requires_explicit_evidence_mode(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["exam", "--model", "test-local"])
    with pytest.raises(SystemExit) as exc:
        child_exam_pipeline.main()
    assert exc.value.code == 2


def test_preflight_cannot_be_combined_with_source_arguments(monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["exam", "--check-local-model", "--auto-evidence", "--model", "test-local"]
    )
    with pytest.raises(SystemExit) as exc:
        child_exam_pipeline.main()
    assert exc.value.code == 2


def test_offline_model_blocks_auto_evidence_fetch_before_network(monkeypatch):
    class _Unavailable(_ReadyLocalModel):
        def check_ready(self):
            raise RuntimeError("local model is not installed")

    monkeypatch.setattr(child_exam_pipeline, "OllamaLocalJsonCallback", _Unavailable)
    monkeypatch.setattr(
        child_exam_pipeline, "fetch_official_guidance_evidence",
        lambda *args, **kwargs: pytest.fail("must fail before evidence network fetch"),
    )
    monkeypatch.setattr(
        sys, "argv", ["exam", "--auto-evidence", "--model", "not-installed"]
    )
    with pytest.raises(RuntimeError, match="not installed"):
        child_exam_pipeline.main()


def test_available_local_model_preserves_existing_evidence_generation(monkeypatch, tmp_path):
    _ReadyLocalModel.calls = []
    monkeypatch.setattr(child_exam_pipeline, "OllamaLocalJsonCallback", _ReadyLocalModel)
    evidence = tmp_path / "evidence.json"
    evidence.write_text(json.dumps({"source": {"passage": "provided"}}), encoding="utf-8")
    captured = {}

    def fake_generate(model, supplied, out, *, items_per_form, version):
        captured.update({
            "model": model.model, "evidence": supplied,
            "items": items_per_form, "out": out, "version": version,
        })
        return {"form_a": tmp_path / "a.docx", "form_b": tmp_path / "b.docx"}

    monkeypatch.setattr(child_exam_pipeline, "generate_child_parallel_docx", fake_generate)
    monkeypatch.setattr(
        sys, "argv",
        ["exam", "--evidence", str(evidence), "--model", "test-local", "--items", "3"],
    )
    child_exam_pipeline.main()
    assert _ReadyLocalModel.calls == [("init", "test-local"), ("ready", "test-local")]
    assert captured["items"] == 3
    assert captured["evidence"] == {"source": {"passage": "provided"}}
