"""Regression tests for slow, zero-fee local Ollama inference configuration.

All tests are offline; they do not claim that a real model ran.
"""

import json
import sys

import pytest

from src import child_exam_pipeline


class RecordingLocalModel:
    constructed = []

    def __init__(self, *, model=None, timeout_seconds=180):
        self.model = model or "local-test"
        self.timeout_seconds = timeout_seconds
        self.constructed.append((self.model, self.timeout_seconds))

    def check_ready(self):
        return self.model

    def __call__(self, request):
        return {"probe": "ok"}


def test_default_timeout_keeps_existing_180_second_behavior(monkeypatch, capsys):
    RecordingLocalModel.constructed = []
    monkeypatch.setattr(child_exam_pipeline, "OllamaLocalJsonCallback", RecordingLocalModel)
    monkeypatch.setattr(
        sys, "argv", ["exam", "--probe-local-inference", "--model", "local-test"]
    )
    child_exam_pipeline.main()
    assert RecordingLocalModel.constructed == [("local-test", 180)]
    assert "probe passed" in capsys.readouterr().out


def test_extended_timeout_applies_to_local_inference_probe(monkeypatch, capsys):
    RecordingLocalModel.constructed = []
    monkeypatch.setattr(child_exam_pipeline, "OllamaLocalJsonCallback", RecordingLocalModel)
    monkeypatch.setattr(
        child_exam_pipeline,
        "fetch_official_guidance_evidence",
        lambda *a, **kw: pytest.fail("Probe must not fetch clinical sources"),
    )
    monkeypatch.setattr(
        child_exam_pipeline,
        "generate_child_parallel_docx",
        lambda *a, **kw: pytest.fail("Probe must not export DOCX"),
    )
    monkeypatch.setattr(
        sys, "argv",
        ["exam", "--probe-local-inference", "--model", "local-test",
         "--timeout-seconds", "600"],
    )
    child_exam_pipeline.main()
    assert RecordingLocalModel.constructed == [("local-test", 600.0)]
    assert "probe passed" in capsys.readouterr().out


def test_generation_forwards_timeout_without_changing_item_count(monkeypatch, tmp_path):
    RecordingLocalModel.constructed = []
    monkeypatch.setattr(child_exam_pipeline, "OllamaLocalJsonCallback", RecordingLocalModel)
    evidence = tmp_path / "source.json"
    evidence.write_text(json.dumps({"sample": {"passage": "sample"}}), encoding="utf-8")
    observed = {}

    def fake_generate(model, source_data, output, *, items_per_form, version):
        observed.update({
            "model": model.model,
            "timeout": model.timeout_seconds,
            "source_data": source_data,
            "items": items_per_form,
            "version": version,
        })
        return {"form_a": tmp_path / "a.docx", "form_b": tmp_path / "b.docx"}

    monkeypatch.setattr(child_exam_pipeline, "generate_child_parallel_docx", fake_generate)
    monkeypatch.setattr(
        sys, "argv",
        ["exam", "--evidence", str(evidence), "--model", "local-test",
         "--items", "20", "--timeout-seconds", "450"],
    )
    child_exam_pipeline.main()
    assert RecordingLocalModel.constructed == [("local-test", 450.0)]
    assert observed["items"] == 20
    assert observed["source_data"] == {"sample": {"passage": "sample"}}


@pytest.mark.parametrize("invalid", ["0", "-1", "601", "nan", "inf"])
def test_invalid_timeout_fails_before_network_or_generation(monkeypatch, invalid):
    monkeypatch.setattr(
        child_exam_pipeline,
        "fetch_official_guidance_evidence",
        lambda *a, **kw: pytest.fail("Invalid timeout must not fetch sources"),
    )
    monkeypatch.setattr(
        child_exam_pipeline,
        "generate_child_parallel_docx",
        lambda *a, **kw: pytest.fail("Invalid timeout must not generate"),
    )
    monkeypatch.setattr(
        sys, "argv",
        ["exam", "--auto-evidence", "--model", "local-test",
         "--timeout-seconds", invalid],
    )
    with pytest.raises(ValueError, match="timeout_seconds"):
        child_exam_pipeline.main()
