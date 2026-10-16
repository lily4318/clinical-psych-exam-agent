from __future__ import annotations

from typing import Any


SYSTEM_INSTRUCTION = """你是一個臺灣臨床心理師國考命題 Agent。只能依據提供的考點摘要與權威來源資訊出題；不可把歷屆題原文改寫成近似題，也不可自行補造診斷準則、治療原則或藥理資訊。若來源不足以支持題目，應回報 source_insufficient，而不是猜測。"""

COMMON_CONSTRAINTS = [
    "題目必須只有一個最佳答案。",
    "四個選項需屬於相同邏輯層次，避免用長度、語氣或絕對化字眼洩漏答案。",
    "不得使用『以上皆是』或『以上皆非』，除非有明確且必要的命題理由。",
    "不得複製或近似改寫歷屆考題原文；只能使用歷屆考點索引來掌握考點與風格。",
    "若涉及 DSM、MI、CBT/RP、神經機制或藥物，解析必須能由提供的權威來源支持。",
    "解析需說明正確答案理由，並逐項說明 A-D 其他選項為何正確或錯誤。",
    "sources 只能填入 source_context 中提供的 source_id。",
    "每題至少引用一筆 requirement=historical_support 的歷屆考點來源與一筆權威知識來源。",
    "所有 requirement=required_all 的 source_id 都必須列入 sources。",
    "若存在 requirement=required_any 的來源，至少一筆 required_any source_id 必須列入 sources。",
    "輸出內容必須是 JSON-compatible object，不要附加 Markdown。",
]

ITEM_REQUIRED_FIELDS = [
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
]


def build_generation_request(
    *,
    spec: dict[str, str],
    form: str,
    item_id: str,
    source_context: list[dict[str, str]],
    target_answer: str | None = None,
) -> dict[str, Any]:
    item_spec = {
        "item_id": item_id,
        "form": form,
        "pair_id": spec["pair_id"],
        "category": spec["category"],
        "core_topic": spec["core_topic"],
        "difficulty": spec["difficulty"],
        "cognitive_level": spec["cognitive_level"],
        "equivalence_note": spec.get("equivalence_note", ""),
    }
    if target_answer:
        item_spec["target_answer_position"] = target_answer

    return {
        "system_instruction": SYSTEM_INSTRUCTION,
        "task": "產生一題四選一單選題，符合臺灣臨床心理師國考風格。",
        "item_spec": item_spec,
        "constraints": COMMON_CONSTRAINTS
        + ["若有 target_answer_position，正確選項必須安排在指定位置。"],
        "source_context": source_context,
        "output_contract": {
            "required_fields": ITEM_REQUIRED_FIELDS,
            "options": ["A", "B", "C", "D"],
            "correct_answer": ["A", "B", "C", "D"],
            "quality_status": "草稿",
        },
    }


def build_pair_generation_request(
    *,
    spec: dict[str, str],
    source_context: list[dict[str, str]],
    form_a_item_id: str,
    form_b_item_id: str,
    form_a_target_answer: str,
    form_b_target_answer: str,
) -> dict[str, Any]:
    return {
        "system_instruction": SYSTEM_INSTRUCTION,
        "task": "同時產生甲卷與乙卷的一組平行題，兩題需等值但情境有實質差異。",
        "pair_spec": {
            "pair_id": spec["pair_id"],
            "category": spec["category"],
            "core_topic": spec["core_topic"],
            "difficulty": spec["difficulty"],
            "cognitive_level": spec["cognitive_level"],
            "equivalence_note": spec.get("equivalence_note", ""),
        },
        "forms": [
            {
                "form": "甲卷",
                "item_id": form_a_item_id,
                "target_answer_position": form_a_target_answer,
            },
            {
                "form": "乙卷",
                "item_id": form_b_item_id,
                "target_answer_position": form_b_target_answer,
            },
        ],
        "constraints": COMMON_CONSTRAINTS
        + [
            "甲乙卷必須測量同一學習目標、同難度與同認知層次。",
            "甲乙卷不可只是改姓名、改數字、改物質名稱或同義改寫；題幹情境與干擾選項設計需有實質差異。",
            "兩題的正確答案位置必須各自符合 target_answer_position。",
            "若來源只足以支持其中一題，也必須回報 source_insufficient，不可為湊成一組而猜測。",
        ],
        "source_context": source_context,
        "output_contract": {
            "type": "object",
            "required": ["pair_id", "form_a", "form_b", "equivalence_notes"],
            "item_required_fields": ITEM_REQUIRED_FIELDS,
        },
    }
