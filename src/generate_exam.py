from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .load_blueprint import load_blueprint, load_parallel_blueprint
from .load_exam_history import (
    known_source_ids,
    load_answer_source_catalog,
    load_historical_index,
    load_knowledge_sources,
    load_official_answer_keys,
    load_official_sources,
    merge_history_with_answers,
)
from .provider import QuestionProvider, StubQuestionProvider
from .source_context import build_source_context, source_ids
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
    answer_sources: list[dict[str, str]],
    knowledge_sources: list[dict[str, str]],
    *,
    version: str = "0.2-source-backed-draft",
) -> dict[str, Any]:
    known = known_source_ids(
        history,
        official_sources,
        answer_sources,
        knowledge_sources,
    )
    items: list[dict] = []

    for spec in pairs:
        context = build_source_context(spec, history, knowledge_sources)
        selected_source_ids = source_ids(context)
        item = provider.generate_item(
            spec=spec,
            form=form,
            item_id=_item_id_for(spec, form),
            source_ids=selected_source_ids,
            source_context=context,
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


def load_generation_data() -> tuple[
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
]:
    history = load_historical_index()
    answers = load_official_answer_keys()
    merged_history = merge_history_with_answers(history, answers)
    return (
        merged_history,
        load_official_sources(),
        load_answer_source_catalog(),
        load_knowledge_sources(),
    )


def generate_parallel_drafts(
    provider: QuestionProvider | None = None,
    *,
    version: str = "0.2-source-backed-draft",
) -> tuple[dict[str, Any], dict[str, Any]]:
    load_blueprint()  # validates repository-level blueprint before generation
    pairs = load_parallel_blueprint()
    history, official_sources, answer_sources, knowledge_sources = load_generation_data()
    provider = provider or StubQuestionProvider()

    form_a = generate_form(
        "甲卷",
        provider,
        pairs,
        history,
        official_sources,
        answer_sources,
        knowledge_sources,
        version=version,
    )
    form_b = generate_form(
        "乙卷",
        provider,
        pairs,
        history,
        official_sources,
        answer_sources,
        knowledge_sources,
        version=version,
    )
    return form_a, form_b


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate source-backed structure drafts. The default provider is a STUB; "
            "inject a real provider in Python for publishable item generation."
        )
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "output",
        help="Directory for draft JSON files.",
    )
    parser.add_argument("--version", default="0.2-source-backed-draft")
    args = parser.parse_args()

    form_a, form_b = generate_parallel_drafts(version=args.version)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "form_a.stub.json").write_text(
        json.dumps(form_a, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (args.out / "form_b.stub.json").write_text(
        json.dumps(form_b, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote source-backed structure drafts to {args.out}")


if __name__ == "__main__":
    main()
