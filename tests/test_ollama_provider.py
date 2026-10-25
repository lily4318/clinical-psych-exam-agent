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
    assert len(handlers) == 2
    assert handlers[0].proxies == {}
    assert isinstance(handlers[1], ollama_provider._NoRedirect)


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


@pytest.mark.parametrize("bad_limit", [0, -1, 4097, True, 1.5, "2048"])
def test_invalid_max_output_tokens_fails_before_transport(bad_limit):
    with pytest.raises(ValueError, match="max_output_tokens"):
        OllamaLocalJsonCallback(model="local-test", max_output_tokens=bad_limit)


def test_optional_output_limit_is_sent_only_when_configured(monkeypatch):
    opener, _ = _inject(monkeypatch, _envelope('{"ok": true}'))
    limited = OllamaLocalJsonCallback(model="local-test", max_output_tokens=3072)
    assert limited({"system_instruction": "rules"}) == {"ok": True}
    bounded_request = json.loads(opener.calls[0][0].data)
    assert bounded_request["options"]["num_predict"] == 3072
    assert bounded_request["options"]["temperature"] == 0
    assert bounded_request["stream"] is False

    default = OllamaLocalJsonCallback(model="local-test")
    assert default({"system_instruction": "rules"}) == {"ok": True}
    default_request = json.loads(opener.calls[1][0].data)
    assert "num_predict" not in default_request["options"]


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


def test_truncated_output_reports_safe_token_counts_without_clinical_text(monkeypatch):
    private_text = "CONFIDENTIAL_CLINICAL_RESPONSE"
    body = json.dumps({
        "message": {"role": "assistant", "content": private_text},
        "done": True, "done_reason": "length",
        "eval_count": 3072, "prompt_eval_count": 1050,
    }).encode("utf-8")
    _inject(monkeypatch, body)
    callback = OllamaLocalJsonCallback(model="local-test", max_output_tokens=3072)
    with pytest.raises(RuntimeError, match="output truncated") as error:
        callback({"system_instruction": "rules"})
    message = str(error.value)
    assert "done_reason=length" in message
    assert "eval_count=3072" in message
    assert "prompt_eval_count=1050" in message
    assert "max_output_tokens=3072" in message
    assert private_text not in message


def test_truncated_output_does_not_trust_unvalidated_usage_fields(monkeypatch):
    body = json.dumps({
        "message": {"content": "PRIVATE"},
        "done": True, "done_reason": "length",
        "eval_count": "SENSITIVE_TEXT", "prompt_eval_count": -5,
    }).encode("utf-8")
    _inject(monkeypatch, body)
    with pytest.raises(RuntimeError, match="incomplete") as error:
        OllamaLocalJsonCallback(model="local-test")({"system_instruction": "rules"})
    assert "eval_count=unknown" in str(error.value)
    assert "prompt_eval_count=unknown" in str(error.value)
    assert "max_output_tokens=unset" in str(error.value)
    assert "SENSITIVE_TEXT" not in str(error.value)


def test_completed_but_malformed_json_is_not_reported_as_token_truncation(monkeypatch):
    _inject(monkeypatch, _envelope('{"pair_id":'))
    with pytest.raises(RuntimeError, match="completed inference but generated malformed JSON") as error:
        OllamaLocalJsonCallback(model="local-test")({"system_instruction": "rules"})
    assert "output truncated" not in str(error.value)


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


@pytest.mark.parametrize("failure", [
    TimeoutError("local inference timed out"),
    URLError(TimeoutError("local inference timed out")),
])
def test_slow_local_inference_timeout_is_not_misreported_as_connection_failure(
    monkeypatch, failure
):
    opener = _Opener(b"", exc=failure)
    monkeypatch.setattr(ollama_provider, "build_opener", lambda *a: opener)
    with pytest.raises(RuntimeError, match="inference timed out after 12 seconds") as error:
        OllamaLocalJsonCallback(
            model="already-installed-local-model", timeout_seconds=12
        )({"system_instruction": "local-only JSON probe"})
    assert "Cannot reach" not in str(error.value)
    assert "maximum 600" in str(error.value)
    assert len(opener.calls) == 1
    assert opener.calls[0][0].full_url == "http://127.0.0.1:11434/api/chat"


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


def test_readiness_accepts_installed_local_model_without_generation(monkeypatch):
    body = json.dumps({"models": [{"name": "qwen2.5:latest"}]}).encode()
    opener, handlers = _inject(monkeypatch, body)
    callback = OllamaLocalJsonCallback(model="qwen2.5")
    assert callback.check_ready() == "qwen2.5"
    assert len(opener.calls) == 1
    request, timeout = opener.calls[0]
    assert request.full_url == "http://127.0.0.1:11434/api/tags"
    assert request.get_method() == "GET"
    assert timeout == 10
    assert handlers[0].proxies == {}
    assert isinstance(handlers[1], ollama_provider._NoRedirect)


def test_readiness_rejects_uninstalled_model_without_download(monkeypatch):
    body = json.dumps({"models": [{"name": "other-model:latest"}]}).encode()
    opener, _ = _inject(monkeypatch, body)
    with pytest.raises(RuntimeError, match="not installed"):
        OllamaLocalJsonCallback(model="qwen2.5").check_ready()
    assert len(opener.calls) == 1
    assert opener.calls[0][0].get_method() == "GET"


@pytest.mark.parametrize("body", [b"", b"not-json", b"[]", b'{"models": {}}'])
def test_readiness_rejects_invalid_local_metadata(monkeypatch, body):
    _inject(monkeypatch, body)
    with pytest.raises(RuntimeError, match="metadata|model list"):
        OllamaLocalJsonCallback(model="qwen2.5").check_ready()


def test_readiness_offline_fails_without_cloud_fallback(monkeypatch):
    opener = _Opener(b"", exc=URLError("local daemon not started"))
    monkeypatch.setattr(ollama_provider, "build_opener", lambda *args: opener)
    with pytest.raises(RuntimeError, match="readiness check failed"):
        OllamaLocalJsonCallback(model="qwen2.5").check_ready()
    assert len(opener.calls) == 1
    assert opener.calls[0][0].full_url.startswith("http://127.0.0.1:11434/")


def test_inference_redirect_handler_refuses_external_destination(monkeypatch):
    """Inference must use the same no-redirect protection as model preflight."""
    from urllib.request import Request

    _opener, handlers = _inject(monkeypatch, _envelope('{"ok": true}'))
    callback = OllamaLocalJsonCallback(model="local-test")
    assert callback({"system_instruction": "rules"}) == {"ok": True}
    redirect_guard = handlers[1]
    original = Request(
        "http://127.0.0.1:11434/api/chat",
        data=b'{"model":"local-test"}',
        method="POST",
    )
    assert redirect_guard.redirect_request(
        original, None, 302, "Found", {},
        "https://example.org/external-inference",
    ) is None


def test_inference_redirect_http_error_stops_without_fallback(monkeypatch):
    """A redirect response is a failure, never permission to use a cloud API."""
    error = HTTPError(
        "http://127.0.0.1:11434/api/chat", 302, "Found",
        {"Location": "https://example.org/external-inference"}, None,
    )
    opener = _Opener(b"", exc=error)
    captured = []

    def fake_build_opener(*handlers):
        captured.extend(handlers)
        return opener

    monkeypatch.setattr(ollama_provider, "build_opener", fake_build_opener)
    with pytest.raises(RuntimeError, match="HTTP 302"):
        OllamaLocalJsonCallback(model="local-test")(
            {"system_instruction": "rules"}
        )
    assert len(opener.calls) == 1
    assert opener.calls[0][0].full_url == "http://127.0.0.1:11434/api/chat"
    assert isinstance(captured[1], ollama_provider._NoRedirect)
