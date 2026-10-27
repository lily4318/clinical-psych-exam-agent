"""Content-free local inference progress telemetry regression (no network)."""

import json

from src import ollama_provider
from src.ollama_provider import OllamaLocalJsonCallback


class _Response:
    def __init__(self, raw):
        self.raw = raw

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit):
        return self.raw[:limit]


class _Opener:
    def __init__(self, raw):
        self.raw = raw

    def open(self, request, *, timeout):
        return _Response(self.raw)


def test_progress_trace_reports_safe_counts_without_clinical_text(monkeypatch, capsys):
    private = "PRIVATE_CLINICAL_PROMPT_AND_ANSWER"
    envelope = {
        "done": True,
        "done_reason": "stop",
        "message": {"content": json.dumps({"ok": True, "note": private})},
        "prompt_eval_count": 156,
        "eval_count": 93,
    }
    raw = json.dumps(envelope).encode("utf-8")
    monkeypatch.setattr(ollama_provider, "build_opener", lambda *args: _Opener(raw))
    request = {
        "system_instruction": private,
        "pair_spec": {"pair_id": "P05"},
        "form": {"form": "乙卷"},
    }
    result = OllamaLocalJsonCallback(model="local-test")(request)
    assert result["note"] == private
    output = capsys.readouterr()
    assert output.out == ""
    assert "[ollama] start pair=P05 form=B" in output.err
    assert "[ollama] complete pair=P05 form=B" in output.err
    assert "prompt_tokens=156" in output.err
    assert "output_tokens=93" in output.err
    assert "elapsed_s=" in output.err
    assert private not in output.err


def test_trace_rejects_untrusted_ids_and_usage_metadata(monkeypatch, capsys):
    private = "PRIVATE_RESPONSE"
    raw = json.dumps({
        "done": True,
        "done_reason": "stop",
        "message": {"content": json.dumps({"note": private})},
        "prompt_eval_count": "PRIVATE_TOKEN_FIELD",
        "eval_count": -1,
    }).encode("utf-8")
    monkeypatch.setattr(ollama_provider, "build_opener", lambda *args: _Opener(raw))
    request = {
        "system_instruction": "rules",
        "pair_spec": {"pair_id": "P05\\nPRIVATE_PAIR_ID"},
        "form": {"form": "not-a-form"},
    }
    assert OllamaLocalJsonCallback(model="local-test")(request)["note"] == private
    err = capsys.readouterr().err
    assert "pair=unknown form=-" in err
    assert "prompt_tokens=unknown" in err
    assert "output_tokens=unknown" in err
    assert "PRIVATE_" not in err
