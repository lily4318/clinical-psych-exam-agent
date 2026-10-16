from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from .prompt_builder import build_generation_request, build_pair_generation_request


class QuestionProvider(Protocol):
    def generate_item(
        self,
        spec: dict[str, str],
        form: str,
        item_id: str,
        source_ids: list[str],
        source_context: list[dict[str, str]] | None = None,
    ) -> dict:
        """Generate one item matching the supplied pair specification."""


class PairQuestionProvider(Protocol):
    def generate_pair(
        self,
        spec: dict[str, str],
        source_context: list[dict[str, str]],
    ) -> dict:
        """Generate a source-grounded parallel pair containing form_a and form_b."""


ANSWER_ORDERS = {
    "甲卷": list("ACBDDBACCADBBDCADABC"),
    "乙卷": list("BDACCADBDBCAACBDCDAB"),
}


def target_answer_for(pair_id: str, form: str) -> str:
    index = int(pair_id[1:]) - 1
    return ANSWER_ORDERS[form][index]


class StubQuestionProvider:
    """Structure-only provider.

    It lets the pipeline, validation, export and parallel-form checks run without
    an LLM API. Generated text is deliberately marked STUB and must never be
    treated as publishable clinical content.
    """

    def generate_item(
        self,
        spec: dict[str, str],
        form: str,
        item_id: str,
        source_ids: list[str],
        source_context: list[dict[str, str]] | None = None,
    ) -> dict:
        answer = target_answer_for(spec["pair_id"], form)
        options = {
            letter: f"[STUB] 選項 {letter}：待由正式題目供應器依考點產生"
            for letter in "ABCD"
        }
        options[answer] = f"[STUB] 選項 {answer}：結構測試用暫定最佳答案"

        return {
            "item_id": item_id,
            "form": form,
            "pair_id": spec["pair_id"],
            "stem": (
                f"[STUB][{form}] 依「{spec['core_topic']}」產生"
                f"{spec['difficulty']}／{spec['cognitive_level']}題目。"
            ),
            "options": options,
            "correct_answer": answer,
            "category": spec["category"],
            "subtopic": spec["core_topic"],
            "difficulty": spec["difficulty"],
            "cognitive_level": spec["cognitive_level"],
            "rationale": {
                "correct": "[STUB] 正式產題後補入具來源依據的正解說明。",
                "A": "[STUB] 待正式解析。",
                "B": "[STUB] 待正式解析。",
                "C": "[STUB] 待正式解析。",
                "D": "[STUB] 待正式解析。",
            },
            "sources": source_ids or ["SOURCE-MISSING"],
            "quality_status": "草稿",
        }


class CallbackQuestionProvider:
    """Adapter for a real model/client supplied by the caller."""

    def __init__(self, callback: Callable[[dict], dict]):
        self.callback = callback

    def generate_item(
        self,
        spec: dict[str, str],
        form: str,
        item_id: str,
        source_ids: list[str],
        source_context: list[dict[str, str]] | None = None,
    ) -> dict:
        request = build_generation_request(
            spec=spec,
            form=form,
            item_id=item_id,
            source_context=source_context or [],
            target_answer=target_answer_for(spec["pair_id"], form),
        )
        item = self.callback(request)
        if not isinstance(item, dict):
            raise TypeError("Question provider callback must return a dict.")
        item.setdefault("sources", source_ids)
        item.setdefault("quality_status", "草稿")
        return item


class CallbackPairQuestionProvider:
    """Adapter that generates both forms of one pair in a single model call."""

    def __init__(self, callback: Callable[[dict], dict]):
        self.callback = callback

    def generate_pair(
        self,
        spec: dict[str, str],
        source_context: list[dict[str, str]],
    ) -> dict:
        request = build_pair_generation_request(
            spec=spec,
            source_context=source_context,
            form_a_item_id=spec["form_a_item"],
            form_b_item_id=spec["form_b_item"],
            form_a_target_answer=target_answer_for(spec["pair_id"], "甲卷"),
            form_b_target_answer=target_answer_for(spec["pair_id"], "乙卷"),
        )
        result = self.callback(request)
        if not isinstance(result, dict):
            raise TypeError("Pair provider callback must return a dict.")
        if not {"form_a", "form_b"}.issubset(result):
            raise ValueError("Pair provider result must contain form_a and form_b.")
        return result
