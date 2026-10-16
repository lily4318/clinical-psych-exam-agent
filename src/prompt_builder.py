from __future__ import annotations

from typing import Any


SYSTEM_INSTRUCTION = """你是一個臺灣臨床心理師國考命題 Agent。只能依據提供的考點摘要與權威來源資訊出題；不可把歷屆題原文改寫成近似題，也不可自行補造診斷準則、治療原則或藥理資訊。若來源不足以支持題目，應回報 source_insufficient，而不是猜測。"""


def build_generation_request(
    *,
    spec: dict[str, str],
    form: str,
    item_id: str,
    source_context: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "system_instruction": SYSTEM_INSTRUCTION,
        "task": "產生一題四選一單選題，符合臺灣臨床心理師國考風格。",
        "item_spec": {
            "item_id": item_id,
            "form": form,
            "pair_id": spec["pair_id"],
            "category": spec["category"],
            "core_topic": spec["core_topic"],
            "difficulty": spec["difficulty"],
            "cognitive_level": spec["cognitive_level"],
            "equivalence_note": spec.get("equivalence_note", ""),
        },
        "constraints": [
            "題目必須只有一個最佳答案。",
            "四個選項需屬於相同邏輯層次，避免用長度、語氣或絕對化字眼洩漏答案。",
            "不得使用『以上皆是』或『以上皆非』，除非有明確且必要的命題理由。",
            "不得複製或近似改寫歷屆考題原文；只能使用歷屆考點索引來掌握考點與風格。",
            "若涉及 DSM、MI、CBT/RP、神經機制或藥物，解析必須能由提供的權威來源支持。",
            "解析需說明正確答案理由，並逐項說明 A-D 其他選項為何正確或錯誤。",
            "甲乙卷同一 pair_id 必須測同一學習目標、同難度與同認知層次，但情境需有實質差異。",
            "輸出內容必須是 JSON-compatible object，不要附加 Markdown。",
        ],
        "source_context": source_context,
        "output_contract": {
            "required_fields": [
                "item_id",
                "form",
                "pair_id",
                "stem",
                "options",
                "correct_answer",
                "category",
                "subtopic",
                "difficulty",
                "cognitive_level",
                "rationale",
                "sources",
                "quality_status",
            ],
            "options": ["A", "B", "C", "D"],
            "correct_answer": ["A", "B", "C", "D"],
            "quality_status": "草稿",
        },
    }
