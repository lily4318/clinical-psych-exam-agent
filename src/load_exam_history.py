from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HISTORY = ROOT / "data" / "historical_exam_index.csv"
DEFAULT_OFFICIAL_SOURCES = ROOT / "data" / "official_sources.csv"

CATEGORY_LABELS = {
    "A": "DSM／診斷分類",
    "B": "衡鑑／危險保護因子",
    "C": "MI／改變動機",
    "D": "CBT／復發預防",
    "E": "生理心理／藥理",
    "F": "三級預防／整合",
}


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_historical_index(path: str | Path | None = None) -> list[dict[str, str]]:
    target = Path(path) if path else DEFAULT_HISTORY
    rows = _load_csv(target)
    required = {
        "item_id",
        "year",
        "source_item",
        "category",
        "subtopic",
        "assessment_focus",
        "difficulty",
        "cognitive_level",
    }
    if not rows:
        raise ValueError("Historical exam index is empty.")
    if not required.issubset(rows[0]):
        raise ValueError("Historical exam index is missing required columns.")
    return rows


def load_official_sources(path: str | Path | None = None) -> list[dict[str, str]]:
    target = Path(path) if path else DEFAULT_OFFICIAL_SOURCES
    rows = _load_csv(target)
    if not rows:
        raise ValueError("Official source index is empty.")
    return rows


def group_history_by_category(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    reverse = {label: code for code, label in CATEGORY_LABELS.items()}
    for row in rows:
        code = reverse.get(row.get("category", ""))
        if code:
            grouped[code].append(row)
    return dict(grouped)


def known_source_ids(
    history: list[dict[str, str]],
    official_sources: list[dict[str, str]] | None = None,
) -> set[str]:
    ids = {row["item_id"] for row in history if row.get("item_id")}
    for row in official_sources or []:
        year = row.get("year") or row.get("年度")
        if year:
            ids.add(f"MOEX-{year}")
    return ids
