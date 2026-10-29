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


def test_local_json_probe_runs_one_real_inference_without_clinical_sources(monkeypatch, capsys):
    """Only the transport is exercised; no generated item is treated as valid."""
    class _Probe(_ReadyLocalModel):
        def __call__(self, request):
            self.calls.append(("inference", request))
            return {"probe": "ok"}

    _ReadyLocalModel.calls = []
    monkeypatch.setattr(child_exam_pipeline, "OllamaLocalJsonCallback", _Probe)
    monkeypatch.setattr(
        child_exam_pipeline, "fetch_official_guidance_evidence",
        lambda *args, **kwargs: pytest.fail("probe must not fetch clinical sources"),
    )
    monkeypatch.setattr(
        child_exam_pipeline, "generate_child_parallel_docx",
        lambda *args, **kwargs: pytest.fail("probe must not create Word files"),
    )
    monkeypatch.setattr(
        sys, "argv", ["exam", "--probe-local-inference", "--model", "test-local"]
    )
    child_exam_pipeline.main()
    assert [call[0] for call in _ReadyLocalModel.calls] == ["init", "ready", "inference"]
    request = _ReadyLocalModel.calls[2][1]
    assert request["task"] == 'Return the JSON object {"probe": "ok"}.'
    assert "clinical exam" in request["system_instruction"]
    assert "inference probe passed" in capsys.readouterr().out


@pytest.mark.parametrize("response", [
    {"probe": "wrong"}, {"other": "ok"}, [], None,
])
def test_local_json_probe_rejects_noncompliant_response_without_export(
    monkeypatch, response
):
    class _Noncompliant(_ReadyLocalModel):
        def __call__(self, request):
            return response

    monkeypatch.setattr(child_exam_pipeline, "OllamaLocalJsonCallback", _Noncompliant)
    monkeypatch.setattr(
        child_exam_pipeline, "generate_child_parallel_docx",
        lambda *args, **kwargs: pytest.fail("probe must not export"),
    )
    monkeypatch.setattr(sys, "argv", ["exam", "--probe-local-inference"])
    with pytest.raises(RuntimeError, match="failed the minimal JSON inference probe"):
        child_exam_pipeline.main()


def test_local_json_probe_propagates_inference_failure_without_fallback(monkeypatch):
    class _FailedInference(_ReadyLocalModel):
        def __call__(self, request):
            raise RuntimeError("local inference unavailable")

    monkeypatch.setattr(child_exam_pipeline, "OllamaLocalJsonCallback", _FailedInference)
    monkeypatch.setattr(
        child_exam_pipeline, "fetch_official_guidance_evidence",
        lambda *args, **kwargs: pytest.fail("no fallback to source fetch"),
    )
    monkeypatch.setattr(sys, "argv", ["exam", "--probe-local-inference"])
    with pytest.raises(RuntimeError, match="local inference unavailable"):
        child_exam_pipeline.main()


@pytest.mark.parametrize("args", [
    ["--probe-local-inference", "--auto-evidence"],
    ["--probe-local-inference", "--evidence", "unused.json"],
    ["--probe-local-inference", "--check-local-model"],
])
def test_local_json_probe_disallows_generation_or_second_diagnostic(monkeypatch, args):
    monkeypatch.setattr(sys, "argv", ["exam", *args])
    with pytest.raises(SystemExit) as exc:
        child_exam_pipeline.main()
    assert exc.value.code == 2


def test_local_json_probe_never_infers_when_model_not_installed(monkeypatch):
    class _Unavailable(_ReadyLocalModel):
        def check_ready(self):
            raise RuntimeError("local model is not installed")

        def __call__(self, request):
            pytest.fail("must not infer when model is unavailable")

    monkeypatch.setattr(child_exam_pipeline, "OllamaLocalJsonCallback", _Unavailable)
    monkeypatch.setattr(sys, "argv", ["exam", "--probe-local-inference"])
    with pytest.raises(RuntimeError, match="not installed"):
        child_exam_pipeline.main()
