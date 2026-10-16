from __future__ import annotations

import json
import os
import re
from typing import Any


_JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.DOTALL | re.IGNORECASE)


def _parse_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    match = _JSON_FENCE_RE.match(cleaned)
    if match:
        cleaned = match.group(1).strip()
    value = json.loads(cleaned)
    if not isinstance(value, dict):
        raise TypeError("Model output must be one JSON object.")
    return value


class OpenAIResponsesJsonCallback:
    """Optional OpenAI Responses API adapter.

    No API key or model name is stored in the repository. By default this class
    reads OPENAI_API_KEY and OPENAI_MODEL from the process environment.
    """

    def __init__(self, *, model: str | None = None, client: Any | None = None):
        self.model = model or os.getenv("OPENAI_MODEL")
        if not self.model:
            raise RuntimeError(
                "OPENAI_MODEL is required. Set it in the environment or pass model=... explicitly."
            )

        if client is not None:
            self.client = client
            return

        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY is required for live generation. Do not commit API keys to GitHub."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                'OpenAI SDK is not installed. Run: pip install -e ".[openai]"'
            ) from exc

        self.client = OpenAI()

    def __call__(self, request: dict[str, Any]) -> dict[str, Any]:
        payload = json.dumps(request, ensure_ascii=False, indent=2)
        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "user",
                    "content": (
                        "依照以下結構化命題要求執行。只輸出一個合法 JSON object，"
                        "不要使用 Markdown code fence，也不要加任何前後說明。\n\n"
                        + payload
                    ),
                }
            ],
        )
        text = getattr(response, "output_text", None)
        if not text:
            raise RuntimeError("OpenAI Responses API returned no output_text.")
        return _parse_json_object(text)
