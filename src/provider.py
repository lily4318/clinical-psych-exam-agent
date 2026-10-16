from __future__ import annotations

from typing import Protocol


class QuestionProvider(Protocol):
    def generate_item(
        self,
        spec: dict[str, str],
        form: str,
        item_id: str,
        source_ids: list[str],
    ) -> dict:
        """Generate one item matching the supplied pair specification."""


ANSWER_ORDERS = {
    "甲卷": list("ACBDDBACCADBBDCADABC"),
    "乙卷": list("BDACCADBDBCAACBDCDAB"),
}


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
    ) -> dict:
        index = int(spec["pair_id"][1:]) - 1
        answer = ANSWER_ORDERS[form][index]
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
