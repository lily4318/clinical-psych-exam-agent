from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from .check_parallel_forms import check_parallel_forms
from .export_exam import export_exam
from .generate_exam import (
    _source_rule_sets,
    _validate_against_spec,
    load_generation_data,
)
from .load_blueprint import (
    load_blueprint,
    load_pair_source_requirements,
    load_parallel_blueprint,
)
from .load_exam_history import (
    CATEGORY_LABELS,
    known_source_ids,
    load_historical_index,
    load_official_answer_keys,
    merge_history_with_answers,
)
from .source_context import build_source_context, source_ids

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "review" / "release_manifest_v0.2.yaml"


def load_review_manifest(path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path) if path else DEFAULT_MANIFEST
    with target.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("Review manifest must contain a mapping.")
    if not data.get("version"):
        raise ValueError("Review manifest requires version.")
    batches = data.get("batches")
    if not isinstance(batches, list) or not batches:
        raise ValueError("Review manifest requires a non-empty batches list.")
    expected = data.get("expected_pairs")
    canonical = [f"P{i:02d}" for i in range(1, 21)]
    if expected != canonical:
        raise ValueError("Review manifest expected_pairs must be exactly P01-P20 in order.")
    return data


def _load_manifest_pairs(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    by_pair: dict[str, dict[str, Any]] = {}
    for rel_path in manifest["batches"]:
        path = ROOT / rel_path
        if not path.exists():
            raise FileNotFoundError(f"Review batch does not exist: {rel_path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("approved_by_user") is True:
            raise ValueError(
                f"{rel_path} is unexpectedly marked approved_by_user=true; "
                "review releases must remain unapproved until explicit user approval."
            )
        for pair in payload.get("pairs", []):
            pair_id = pair.get("pair_id")
            if not pair_id:
                raise ValueError(f"Missing pair_id in {rel_path}.")
            if pair_id in by_pair:
                raise ValueError(f"Duplicate pair_id across review batches: {pair_id}")
            if not isinstance(pair.get("form_a"), dict) or not isinstance(pair.get("form_b"), dict):
                raise ValueError(f"{pair_id} must contain form_a and form_b objects.")
            by_pair[pair_id] = pair

    expected = manifest["expected_pairs"]
    if set(by_pair) != set(expected):
        missing = sorted(set(expected) - set(by_pair))
        extra = sorted(set(by_pair) - set(expected))
        raise ValueError(f"Review batches do not cover P01-P20. missing={missing}, extra={extra}")
    return [by_pair[pair_id] for pair_id in expected]


def assemble_review_release(
    manifest_path: str | Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    manifest = load_review_manifest(manifest_path)
    review_pairs = _load_manifest_pairs(manifest)
    blueprint = load_blueprint()
    pair_specs = load_parallel_blueprint()
    source_requirements = load_pair_source_requirements()
    _, official_sources, answer_sources, knowledge_sources = load_generation_data()
    # The canonical review-v0.2 references pre-111 historical items. Use the
    # full audited history for this frozen review snapshot, while new drafts
    # continue to use the rolling five-year window in load_generation_data().
    history = merge_history_with_answers(
        load_historical_index(), load_official_answer_keys()
    )

    known = known_source_ids(
        history,
        official_sources,
        answer_sources,
        knowledge_sources,
    )
    knowledge_ids = {
        row["source_id"] for row in knowledge_sources if row.get("source_id")
    }

    review_by_pair = {pair["pair_id"]: pair for pair in review_pairs}
    errors: list[str] = []
    form_a_items: list[dict] = []
    form_b_items: list[dict] = []

    for spec in pair_specs:
        pair_id = spec["pair_id"]
        pair = review_by_pair[pair_id]
        required_all, required_any = _source_rule_sets(
            spec, source_requirements
        )
        context = build_source_context(
            spec,
            history,
            knowledge_sources,
            required_all_source_ids=required_all,
            required_any_source_ids=required_any,
        )
        context_ids = set(source_ids(context))
        selected_knowledge = context_ids & knowledge_ids

        # Human-reviewed batches may intentionally cite a relevant historical
        # item that did not land in the automatic top-N similarity selection.
        # Keep historical citations restricted to the same blueprint category,
        # while authoritative knowledge sources remain pair-specific and strict.
        category_label = CATEGORY_LABELS[spec["category"]]
        category_historical = {
            row["item_id"]
            for row in history
            if row.get("item_id") and row.get("category") == category_label
        }
        allowed = category_historical | selected_knowledge

        for key, form, target in (
            ("form_a", "甲卷", form_a_items),
            ("form_b", "乙卷", form_b_items),
        ):
            item = pair[key]
            item_errors = _validate_against_spec(
                item,
                spec,
                form,
                known,
                allowed_source_ids=allowed,
                historical_source_ids=category_historical,
                knowledge_source_ids=selected_knowledge,
                required_all_source_ids=required_all,
                required_any_source_ids=required_any,
            )
            errors.extend(f"{pair_id} {form}: {error}" for error in item_errors)
            target.append(item)

    common = {
        "version": manifest["version"],
        "quality_status": manifest.get("status", "待複核"),
        "approved_by_user": False,
    }
    form_a = {"form": "甲卷", "items": form_a_items, **common}
    form_b = {"form": "乙卷", "items": form_b_items, **common}

    structural = check_parallel_forms(
        form_a,
        form_b,
        blueprint,
        pair_specs,
        known,
    )
    errors.extend(structural["errors"])

    report = {
        "ok": not errors,
        "version": manifest["version"],
        "manifest": str(Path(manifest_path) if manifest_path else DEFAULT_MANIFEST.relative_to(ROOT)),
        "errors": errors,
        "warnings": structural["warnings"],
        "metrics": structural["forms"],
    }
    return form_a, form_b, report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assemble the canonical P01-P20 human-review release and validate it."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--out", type=Path, default=ROOT / "output" / "review-v0.2")
    args = parser.parse_args()

    form_a, form_b, report = assemble_review_release(args.manifest)
    if not report["ok"]:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        raise SystemExit(1)

    args.out.mkdir(parents=True, exist_ok=True)
    export_exam(form_a, args.out)
    export_exam(form_b, args.out)
    (args.out / "review_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
