from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .load_blueprint import (
    load_blueprint,
    load_pair_source_requirements,
    load_parallel_blueprint,
)
from .load_exam_history import (
    known_source_ids,
    load_answer_source_catalog,
    load_knowledge_sources,
    load_official_answer_keys,
    load_official_sources,
    load_recent_historical_index,
    merge_history_with_answers,
)
from .provider import (
    PairQuestionProvider,
    QuestionProvider,
    StubQuestionProvider,
    target_answer_for,
)
from .source_context import build_source_context, source_ids
from .validate_item import validate_item

ROOT = Path(__file__).resolve().parents[1]


def _item_id_for(spec: dict[str, str], form: str) -> str:
    return spec["form_a_item"] if form == "甲卷" else spec["form_b_item"]


def _validate_against_spec(
    item: dict,
    spec: dict[str, str],
    form: str,
    known_sources: set[str],
    *,
    allowed_source_ids: set[str] | None = None,
    historical_source_ids: set[str] | None = None,
    knowledge_source_ids: set[str] | None = None,
    required_all_source_ids: set[str] | None = None,
    required_any_source_ids: set[str] | None = None,
) -> list[str]:
    errors = validate_item(item, known_sources)
    expected = {
        "item_id": _item_id_for(spec, form),
        "form": form,
        "pair_id": spec["pair_id"],
        "category": spec["category"],
        "difficulty": spec["difficulty"],
        "cognitive_level": spec["cognitive_level"],
        "correct_answer": target_answer_for(spec["pair_id"], form),
    }
    for field, value in expected.items():
        if item.get(field) != value:
            errors.append(f"{field} must equal {value!r} for {spec['pair_id']} {form}.")

    cited = set(item.get("sources") or [])
    if allowed_source_ids is not None:
        disallowed = sorted(cited - allowed_source_ids)
        if disallowed:
            errors.append(
                "Item cites sources outside this pair's selected source context: "
                + ", ".join(disallowed)
            )

    if historical_source_ids is not None and not (cited & historical_source_ids):
        errors.append("Item must cite at least one selected historical exam-index source.")
    if knowledge_source_ids is not None and not (cited & knowledge_source_ids):
        errors.append("Item must cite at least one selected authoritative knowledge source.")

    required_all = required_all_source_ids or set()
    missing_required = sorted(required_all - cited)
    if missing_required:
        errors.append(
            "Item is missing required core sources: " + ", ".join(missing_required)
        )

    required_any = required_any_source_ids or set()
    if required_any and not (cited & required_any):
        errors.append(
            "Item must cite at least one of these core sources: "
            + ", ".join(sorted(required_any))
        )

    return errors


def _source_rule_sets(
    spec: dict[str, str],
    source_requirements: dict[str, dict[str, list[str]]],
) -> tuple[set[str], set[str]]:
    rules = source_requirements[spec["pair_id"]]
    required_all = set(rules.get("require_all") or [])
    required_any = set(rules.get("require_any") or [])
    return required_all, required_any


def generate_form(
    form: str,
    provider: QuestionProvider,
    pairs: list[dict[str, str]],
    history: list[dict[str, str]],
    official_sources: list[dict[str, str]],
    answer_sources: list[dict[str, str]],
    knowledge_sources: list[dict[str, str]],
    source_requirements: dict[str, dict[str, list[str]]],
    *,
    version: str = "0.2-source-backed-draft",
) -> dict[str, Any]:
    known = known_source_ids(
        history,
        official_sources,
        answer_sources,
        knowledge_sources,
    )
    historical_ids = {row["item_id"] for row in history if row.get("item_id")}
    knowledge_ids = {
        row["source_id"] for row in knowledge_sources if row.get("source_id")
    }
    items: list[dict] = []

    for spec in pairs:
        required_all, required_any = _source_rule_sets(spec, source_requirements)
        context = build_source_context(
            spec,
            history,
            knowledge_sources,
            required_all_source_ids=required_all,
            required_any_source_ids=required_any,
        )
        selected_source_ids = source_ids(context)
        allowed = set(selected_source_ids)
        selected_historical = allowed & historical_ids
        selected_knowledge = allowed & knowledge_ids
        item = provider.generate_item(
            spec=spec,
            form=form,
            item_id=_item_id_for(spec, form),
            source_ids=selected_source_ids,
            source_context=context,
        )
        errors = _validate_against_spec(
            item,
            spec,
            form,
            known,
            allowed_source_ids=allowed,
            historical_source_ids=selected_historical,
            knowledge_source_ids=selected_knowledge,
            required_all_source_ids=required_all,
            required_any_source_ids=required_any,
        )
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
    # New simulation generation uses the latest five available exam years.
    # Older indexed years remain in the repository for audit and formal-release history.
    history = load_recent_historical_index(count=5)
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
    load_blueprint()
    pairs = load_parallel_blueprint()
    source_requirements = load_pair_source_requirements()
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
        source_requirements,
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
        source_requirements,
        version=version,
    )
    return form_a, form_b


def generate_parallel_pairs(
    provider: PairQuestionProvider,
    *,
    version: str = "0.2-source-backed-draft",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Generate both forms pair-by-pair so the model can enforce equivalence directly."""
    load_blueprint()
    pairs = load_parallel_blueprint()
    source_requirements = load_pair_source_requirements()
    history, official_sources, answer_sources, knowledge_sources = load_generation_data()
    known = known_source_ids(
        history,
        official_sources,
        answer_sources,
        knowledge_sources,
    )
    historical_ids = {row["item_id"] for row in history if row.get("item_id")}
    knowledge_ids = {
        row["source_id"] for row in knowledge_sources if row.get("source_id")
    }

    form_a_items: list[dict] = []
    form_b_items: list[dict] = []

    for spec in pairs:
        required_all, required_any = _source_rule_sets(spec, source_requirements)
        context = build_source_context(
            spec,
            history,
            knowledge_sources,
            required_all_source_ids=required_all,
            required_any_source_ids=required_any,
        )
        selected_source_ids = source_ids(context)
        allowed = set(selected_source_ids)
        selected_historical = allowed & historical_ids
        selected_knowledge = allowed & knowledge_ids
        result = provider.generate_pair(spec, context)

        for key, form, target in (
            ("form_a", "甲卷", form_a_items),
            ("form_b", "乙卷", form_b_items),
        ):
            item = result[key]
            if not isinstance(item, dict):
                raise TypeError(f"{spec['pair_id']} {key} must be a dict.")
            item.setdefault("sources", selected_source_ids)
            item.setdefault("quality_status", "草稿")
            errors = _validate_against_spec(
                item,
                spec,
                form,
                known,
                allowed_source_ids=allowed,
                historical_source_ids=selected_historical,
                knowledge_source_ids=selected_knowledge,
                required_all_source_ids=required_all,
                required_any_source_ids=required_any,
            )
            if errors:
                raise ValueError(
                    f"{spec['pair_id']} {form}: " + "; ".join(errors)
                )
            target.append(item)

    common = {"version": version, "quality_status": "草稿", "approved_by_user": False}
    return (
        {"form": "甲卷", "items": form_a_items, **common},
        {"form": "乙卷", "items": form_b_items, **common},
    )


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
