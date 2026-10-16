from __future__ import annotations

import re
from typing import Iterable

CATEGORY_DOMAINS = {
    "A": {"DSM"},
    "B": {"ASSESSMENT", "DSM"},
    "C": {"MI"},
    "D": {"CBT"},
    "E": {"NEURO", "PHARM"},
    "F": {"ASSESSMENT", "CBT"},
}


def _terms(text: str) -> list[str]:
    parts = re.split(r"[／/、，,：:；;（）()\s]+", text or "")
    return [part.strip().lower() for part in parts if len(part.strip()) >= 2]


def _history_score(spec: dict[str, str], row: dict[str, str]) -> tuple[int, int]:
    haystack = " ".join(
        [row.get("subtopic", ""), row.get("assessment_focus", "")]
    ).lower()
    score = sum(2 if term in haystack else 0 for term in _terms(spec.get("core_topic", "")))
    if row.get("difficulty") == spec.get("difficulty"):
        score += 1
    if row.get("cognitive_level") == spec.get("cognitive_level"):
        score += 1
    try:
        year = int(row.get("year", "0"))
    except ValueError:
        year = 0
    return score, year


def select_history_sources(
    spec: dict[str, str],
    history: list[dict[str, str]],
    *,
    limit: int = 4,
) -> list[dict[str, str]]:
    label_by_code = {
        "A": "DSM／診斷分類",
        "B": "衡鑑／危險保護因子",
        "C": "MI／改變動機",
        "D": "CBT／復發預防",
        "E": "生理心理／藥理",
        "F": "三級預防／整合",
    }
    category_label = label_by_code[spec["category"]]
    candidates = [row for row in history if row.get("category") == category_label]
    candidates.sort(key=lambda row: _history_score(spec, row), reverse=True)
    return candidates[:limit]


def select_knowledge_sources(
    spec: dict[str, str],
    knowledge_sources: list[dict[str, str]],
    *,
    limit: int = 4,
) -> list[dict[str, str]]:
    domains = CATEGORY_DOMAINS.get(spec["category"], set())
    candidates = [row for row in knowledge_sources if row.get("domain") in domains]

    authority_rank = {"high": 3, "medium_high": 2, "medium": 1}
    candidates.sort(
        key=lambda row: authority_rank.get(row.get("authority", ""), 0),
        reverse=True,
    )
    return candidates[:limit]


def build_source_context(
    spec: dict[str, str],
    history: list[dict[str, str]],
    knowledge_sources: list[dict[str, str]],
) -> list[dict[str, str]]:
    context: list[dict[str, str]] = []

    for row in select_history_sources(spec, history):
        context.append(
            {
                "source_id": row["item_id"],
                "kind": "historical_exam_index",
                "title": f"{row['year']} 年 {row['source_item']} 歷屆考點索引",
                "organization": "考選部（題目來源）／本 Agent 摘要索引",
                "url": "",
                "usage_notes": row.get("assessment_focus", ""),
            }
        )

    for row in select_knowledge_sources(spec, knowledge_sources):
        context.append(
            {
                "source_id": row["source_id"],
                "kind": row.get("source_type", "knowledge_source"),
                "title": row.get("title", ""),
                "organization": row.get("organization", ""),
                "url": row.get("url", ""),
                "usage_notes": row.get("usage_notes", ""),
            }
        )

    return context


def source_ids(context: Iterable[dict[str, str]]) -> list[str]:
    return [row["source_id"] for row in context if row.get("source_id")]
