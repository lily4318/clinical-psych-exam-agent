from __future__ import annotations

import argparse
import json
from pathlib import Path

from .check_parallel_forms import check_parallel_forms
from .export_exam import export_exam
from .generate_exam import generate_parallel_pairs
from .load_blueprint import load_blueprint, load_parallel_blueprint
from .load_exam_history import (
    known_source_ids,
    load_answer_source_catalog,
    load_historical_index,
    load_knowledge_sources,
    load_official_sources,
)
from .openai_provider import OpenAIResponsesJsonCallback
from .provider import CallbackPairQuestionProvider

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate and validate source-backed parallel exam forms with the OpenAI Responses API."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "output" / "openai-draft",
        help="Output directory for JSON, Markdown and validation report.",
    )
    parser.add_argument("--version", default="0.3-openai-draft")
    parser.add_argument(
        "--model",
        default=None,
        help="Optional model override. Otherwise OPENAI_MODEL is required.",
    )
    args = parser.parse_args()

    callback = OpenAIResponsesJsonCallback(model=args.model)
    provider = CallbackPairQuestionProvider(callback)
    form_a, form_b = generate_parallel_pairs(provider, version=args.version)

    known = known_source_ids(
        load_historical_index(),
        load_official_sources(),
        load_answer_source_catalog(),
        load_knowledge_sources(),
    )
    report = check_parallel_forms(
        form_a,
        form_b,
        load_blueprint(),
        load_parallel_blueprint(),
        known,
    )

    args.out.mkdir(parents=True, exist_ok=True)
    report_path = args.out / "parallel_form_check.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if not report["ok"]:
        raise SystemExit(
            "Generated forms failed validation. See: " + str(report_path)
        )

    export_exam(form_a, args.out)
    export_exam(form_b, args.out)
    print(f"Generated and validated both forms in {args.out}")
    if report["warnings"]:
        print("Validation warnings:")
        for warning in report["warnings"]:
            print(f"- {warning}")


if __name__ == "__main__":
    main()
