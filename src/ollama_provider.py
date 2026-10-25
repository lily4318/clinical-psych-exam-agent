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
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

_LOCAL_CHAT_URL = "http://127.0.0.1:11434/api/chat"
_LOCAL_TAGS_URL = "http://127.0.0.1:11434/api/tags"
_MAX_RESPONSE_BYTES = 4 * 1024 * 1024
_MAX_TAGS_BYTES = 1024 * 1024


class _NoRedirect(HTTPRedirectHandler):
    """A local readiness probe must never follow redirects to external hosts."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


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

    def check_ready(self) -> str:
        """Confirm this exact model is already installed locally; never pull it.

        This is an optional no-inference, no-paid-API preflight. Ollama's
        /api/tags endpoint lists local models only; no model generation occurs.
        """
        request = Request(_LOCAL_TAGS_URL, method="GET")
        opener = build_opener(ProxyHandler({}), _NoRedirect())
        try:
            with opener.open(request, timeout=min(self.timeout_seconds, 10.0)) as response:
                raw = response.read(_MAX_TAGS_BYTES + 1)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise RuntimeError(
                "Local Ollama readiness check failed at 127.0.0.1:11434. "
                "Start the local Ollama server; no cloud or paid fallback was used."
            ) from exc
        if not raw or len(raw) > _MAX_TAGS_BYTES:
            raise RuntimeError("Local Ollama returned empty or oversized model metadata.")
        try:
            data = json.loads(raw)
        except (ValueError, TypeError) as exc:
            raise RuntimeError("Local Ollama returned invalid model metadata.") from exc
        if not isinstance(data, dict) or not isinstance(data.get("models"), list):
            raise RuntimeError("Local Ollama model list is malformed.")
        installed = {
            value.strip()
            for row in data["models"]
            if isinstance(row, dict)
            for value in (row.get("name"), row.get("model"))
            if isinstance(value, str) and value.strip()
        }
        requested = self.model
        normalized = requested if ":" in requested else requested + ":latest"
        if requested not in installed and normalized not in installed:
            raise RuntimeError(
                f"Local model {requested!r} is not installed. "
                "Install a suitable model locally first; no download or paid "
                "model API is invoked automatically."
            )
        return requested

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

        # Reject redirects during inference as well as readiness checks.
        # Otherwise a local HTTP redirect could forward the clinical prompt
        # to an external service despite the fixed loopback request URL.
        opener = build_opener(ProxyHandler({}), _NoRedirect())
        try:
            with opener.open(http_request, timeout=self.timeout_seconds) as response:
                raw = response.read(_MAX_RESPONSE_BYTES + 1)
        except HTTPError as exc:
            raise RuntimeError(
                f"Local Ollama returned HTTP {exc.code}. Check that "
                f"model {self.model!r} is already downloaded and loaded locally."
            ) from exc
        except (URLError, TimeoutError, OSError) as exc:
            # urllib may wrap a socket timeout inside URLError.  A slow local
            # inference is not the same failure as an unreachable server.
            if isinstance(exc, TimeoutError) or (
                isinstance(exc, URLError)
                and isinstance(exc.reason, TimeoutError)
            ):
                raise RuntimeError(
                    f"Local Ollama inference timed out after {self.timeout_seconds:g} "
                    "seconds. Increase --timeout-seconds (maximum 600), or use "
                    "a faster already-installed local model. No paid fallback "
                    "was attempted."
                ) from exc
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
