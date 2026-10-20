"""Strict, local-only JSON callback for an Ollama model already installed by the user.

This is an inference *transport*, not a question validator or an agent. It never
downloads a model, contacts Ollama Cloud, starts a server, or uses a paid API.
"""

from __future__ import annotations

import json
import math
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener

_LOCAL_CHAT_URL = "http://127.0.0.1:11434/api/chat"
_MAX_RESPONSE_BYTES = 4 * 1024 * 1024


class OllamaLocalJsonCallback:
    """Bridge existing structured generation requests to local Ollama chat.

    Pass this callback to CallbackPairQuestionProvider. Downstream domain-specific
    source validation, clinical review and Word export remain separate gates.
    """

    def __init__(self, *, model: str | None = None, timeout_seconds: float = 180):
        selected = model if model is not None else os.getenv("OLLAMA_MODEL", "")
        if not isinstance(selected, str) or not selected.strip():
            raise RuntimeError(
                "A local model name is required. Set OLLAMA_MODEL or pass model=...; "
                "no Stub or paid API fallback is permitted."
            )
        # Ollama also supports cloud-backed model labels; prohibit all cloud
        # labels in this strictly local, zero-additional-fee backend.
        if "cloud" in selected.casefold():
            raise ValueError("Cloud-backed models are not allowed in local-only mode.")
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, (float, int))
            or not math.isfinite(timeout_seconds)
            or not 1 <= timeout_seconds <= 600
        ):
            raise ValueError("timeout_seconds must be between 1 and 600.")
        self.model = selected.strip()
        self.timeout_seconds = float(timeout_seconds)

    def __call__(self, request: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(request, dict):
            raise TypeError("Generation request must be a JSON-compatible dictionary.")
        system = request.get("system_instruction")
        if not isinstance(system, str) or not system.strip():
            raise ValueError("Generation request requires system_instruction.")

        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
            "messages": [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": (
                        "遵守以下結構化命題要求，只回傳一個合法 JSON object。"
                        "若臨床來源不足，請回報 source_insufficient=true，"
                        "絕不猜測或捏造引用。\n\n"
                        + json.dumps(request, ensure_ascii=False)
                    ),
                },
            ],
        }
        http_request = Request(
            _LOCAL_CHAT_URL,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        # Disable all proxy forwarding. Fixed loopback URL is not user-supplied.
        opener = build_opener(ProxyHandler({}))
        try:
            with opener.open(http_request, timeout=self.timeout_seconds) as response:
                raw = response.read(_MAX_RESPONSE_BYTES + 1)
        except HTTPError as exc:
            raise RuntimeError(
                f"Local Ollama returned HTTP {exc.code}. Check that "
                f"model {self.model!r} is already downloaded and loaded locally."
            ) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise RuntimeError(
                "Cannot reach the local Ollama server at 127.0.0.1:11434. "
                "Install/start Ollama and a locally downloaded model first. "
                "GitHub-hosted Actions cannot reach your computer's localhost."
            ) from exc

        if not raw or len(raw) > _MAX_RESPONSE_BYTES:
            raise RuntimeError("Local Ollama returned an empty or oversized response.")
        try:
            envelope = json.loads(raw)
            if not isinstance(envelope, dict):
                raise ValueError("response envelope is not a JSON object")
            if envelope.get("done") is not True or envelope.get("done_reason") == "length":
                raise ValueError("incomplete response")
            message = envelope.get("message")
            if not isinstance(message, dict) or not isinstance(message.get("content"), str):
                raise ValueError("missing assistant message content")
            result = json.loads(message["content"])
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise RuntimeError(
                "Local Ollama returned malformed or incomplete structured JSON. "
                "Do not export or approve the resulting questions."
            ) from exc

        if not isinstance(result, dict):
            raise RuntimeError("Local model output must be one JSON object.")
        if result.get("source_insufficient"):
            raise RuntimeError(
                "Local model reported source_insufficient; generation stopped. "
                "Verify source text before generating clinical questions."
            )
        return result
