"""No-network regression tests for the local-only Ollama JSON transport."""

import json
from urllib.error import HTTPError, URLError

import pytest

from src import ollama_provider
from src.ollama_provider import OllamaLocalJsonCallback


class _Response:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit):
        return self.body[:limit]


class _Opener:
    def __init__(self, body, exc=None):
        self.body = body
        self.exc = exc
        self.calls = []

    def open(self, request, *, timeout):
        self.calls.append((request, timeout))
        if self.exc:
            raise self.exc
        return _Response(self.body)


def _envelope(content, *, done=True, reason="stop"):
    return json.dumps(
        {"message": {"role": "assistant", "content": content}, "done": done,
         "done_reason": reason},
        ensure_ascii=False,
    ).encode("utf-8")


def _inject(monkeypatch, response):
    opener = _Opener(response)
    captured = []

    def fake_build_opener(*handlers):
        captured.extend(handlers)
        return opener

    monkeypatch.setattr(ollama_provider, "build_opener", fake_build_opener)
    return opener, captured


def test_local_callback_uses_fixed_loopback_and_structured_json(monkeypatch):
    answer = {"pair_id": "P01", "form_a": {}, "form_b": {}}
    opener, handlers = _inject(monkeypatch, _envelope(json.dumps(answer)))
    callback = OllamaLocalJsonCallback(model="local-test-model", timeout_seconds=30)
    assert callback({"system_instruction": "你是國考命題 Agent", "task": "測試"}) == answer

    assert len(opener.calls) == 1
    request, timeout = opener.calls[0]
    assert request.full_url == "http://127.0.0.1:11434/api/chat"
    assert request.get_method() == "POST"
    assert timeout == 30
    sent = json.loads(request.data)
    assert sent["model"] == "local-test-model"
    assert sent["format"] == "json"
    assert sent["stream"] is False
    assert sent["options"]["temperature"] == 0
    assert sent["messages"][0]["role"] == "system"
    assert "測試" in sent["messages"][1]["content"]
    assert len(handlers) == 1
    assert handlers[0].proxies == {}


def test_model_can_be_configured_by_environment(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "already-local-model")
    callback = OllamaLocalJsonCallback()
    assert callback.model == "already-local-model"


@pytest.mark.parametrize("model", ["", "   ", None])
def test_missing_model_fails_without_model_or_paid_fallback(monkeypatch, model):
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    with pytest.raises(RuntimeError, match="local model name is required"):
        OllamaLocalJsonCallback(model=model)


@pytest.mark.parametrize("model", ["gpt-test:cloud", "another-CLOUD"])
def test_cloud_model_labels_are_disallowed(model):
    with pytest.raises(ValueError, match="Cloud-backed"):
        OllamaLocalJsonCallback(model=model)


@pytest.mark.parametrize("timeout", [0, -3, 601, float("inf"), float("nan"), True])
def test_invalid_timeout_is_rejected(timeout):
    with pytest.raises(ValueError, match="timeout_seconds"):
        OllamaLocalJsonCallback(model="local-test", timeout_seconds=timeout)


def test_source_insufficient_is_not_accepted_as_generated_content(monkeypatch):
    _inject(monkeypatch, _envelope('{"source_insufficient": true}'))
    callback = OllamaLocalJsonCallback(model="local-test")
    with pytest.raises(RuntimeError, match="source_insufficient"):
        callback({"system_instruction": "rules"})


@pytest.mark.parametrize("content", ['[]', 'not JSON', '42', 'null'])
def test_non_object_or_invalid_generated_json_is_rejected(monkeypatch, content):
    _inject(monkeypatch, _envelope(content))
    callback = OllamaLocalJsonCallback(model="local-test")
    with pytest.raises(RuntimeError, match="JSON|object"):
        callback({"system_instruction": "rules"})


@pytest.mark.parametrize("done,reason", [(False, "stop"), (True, "length")])
def test_incomplete_reply_is_rejected(monkeypatch, done, reason):
    _inject(monkeypatch, _envelope('{"ok": true}', done=done, reason=reason))
    callback = OllamaLocalJsonCallback(model="local-test")
    with pytest.raises(RuntimeError, match="incomplete"):
        callback({"system_instruction": "rules"})


def test_connection_failure_is_explicit_and_never_switches_to_paid_api(monkeypatch):
    opener = _Opener(b"", exc=URLError("server unavailable"))
    monkeypatch.setattr(ollama_provider, "build_opener", lambda *a: opener)
    with pytest.raises(RuntimeError, match="Cannot reach the local Ollama server"):
        OllamaLocalJsonCallback(model="local-test")({"system_instruction": "rules"})


def test_unknown_local_model_reports_http_error(monkeypatch):
    error = HTTPError("http://127.0.0.1:11434/api/chat", 404, "Not Found", {}, None)
    opener = _Opener(b"", exc=error)
    monkeypatch.setattr(ollama_provider, "build_opener", lambda *a: opener)
    with pytest.raises(RuntimeError, match="HTTP 404"):
        OllamaLocalJsonCallback(model="not-installed")({"system_instruction": "rules"})


def test_missing_system_instruction_fails_before_transport(monkeypatch):
    _inject(monkeypatch, _envelope('{"ok": true}'))
    with pytest.raises(ValueError, match="system_instruction"):
        OllamaLocalJsonCallback(model="local-test")({"task": "missing rules"})
