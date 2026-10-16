from types import SimpleNamespace

from src.openai_provider import OpenAIResponsesJsonCallback, _parse_json_object


class _FakeResponses:
    def __init__(self, output_text: str):
        self.output_text = output_text
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text=self.output_text)


class _FakeClient:
    def __init__(self, output_text: str):
        self.responses = _FakeResponses(output_text)


def test_parse_json_object_accepts_plain_json_and_code_fence():
    assert _parse_json_object('{"ok": true}') == {"ok": True}
    assert _parse_json_object('```json\n{"ok": true}\n```') == {"ok": True}


def test_openai_callback_uses_responses_api_and_returns_object():
    client = _FakeClient('{"pair_id":"P01","form_a":{},"form_b":{},"equivalence_notes":"ok"}')
    callback = OpenAIResponsesJsonCallback(model="test-model", client=client)
    result = callback({"task": "test"})

    assert result["pair_id"] == "P01"
    assert len(client.responses.calls) == 1
    call = client.responses.calls[0]
    assert call["model"] == "test-model"
    assert call["input"][0]["role"] == "user"
