from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .load_blueprint import load_blueprint, load_parallel_blueprint
from .load_exam_history import (
    group_history_by_category,
    known_source_ids,
    load_historical_index,
    load_official_sources,
)
from .provider import QuestionProvider, StubQuestionProvider
from .validate_item import validate_item

ROOT = Path(__file__).resolve().parents[1]


def _item_id_for(spec: dict[str, str], form: str) -> str:
    return spec["form_a_item"] if form == "甲卷" else spec["form_b_item"]


def generate_form(
    form: str,
    provider: QuestionProvider,
    pairs: list[dict[str, str]],
    history: list[dict[str, str]],
    official_sources: list[dict[str, str]],
    *,
    version: str = "0.1-draft",
) -> dict[str, Any]:
    grouped = group_history_by_category(history)
    known = known_source_ids(history, official_sources)
    items: list[dict] = []

    for spec in pairs:
        history_rows = grouped.get(spec["category"], [])
        source_ids = [row["item_id"] for row in history_rows[:3]]
        item = provider.generate_item(
            spec=spec,
            form=form,
            item_id=_item_id_for(spec, form),
            source_ids=source_ids,
        )
        errors = validate_item(item, known)
        if errors:
            raise ValueError(f"{item.get('item_id')}: " + "; ".join(errors))
        items.append(item)

    return {
        "form": form,
        "version": version,
        "items": items,
        "quality_status": "草稿",
        "approved_by_user": False,
    }


def generate_parallel_drafts(
    provider: QuestionProvider | None = None,
    *,
    version: str = "0.1-draft",
) -> tuple[dict[str, Any], dict[str, Any]]:
    load_blueprint()  # validates repository-level blueprint before generation
    pairs = load_parallel_blueprint()
    history = load_historical_index()
    official_sources = load_official_sources()
    provider = provider or StubQuestionProvider()

    form_a = generate_form("甲卷", provider, pairs, history, official_sources, version=version)
    form_b = generate_form("乙卷", provider, pairs, history, official_sources, version=version)
    return form_a, form_b


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate structure-only parallel exam drafts. No API key is required."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "output",
        help="Directory for draft JSON files.",
    )
    parser.add_argument("--version", default="0.1-draft")
    args = parser.parse_args()

    form_a, form_b = generate_parallel_drafts(version=args.version)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "form_a.stub.json").write_text(
        json.dumps(form_a, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (args.out / "form_b.stub.json").write_text(
        json.dumps(form_b, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote structure-only drafts to {args.out}")


if __name__ == "__main__":
    main()
