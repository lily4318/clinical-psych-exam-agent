from __future__ import annotations

import argparse
import json
from pathlib import Path

from .load_blueprint import load_parallel_blueprint
from .load_exam_history import load_historical_index, load_knowledge_sources
from .prompt_builder import build_pair_generation_request
from .provider import target_answer_for
from .source_context import build_source_context

ROOT = Path(__file__).resolve().parents[1]


def build_prompt_pack() -> list[dict]:
    pairs = load_parallel_blueprint()
    history = load_historical_index()
    knowledge = load_knowledge_sources()
    pack: list[dict] = []

    for spec in pairs:
        context = build_source_context(spec, history, knowledge)
        pack.append(
            build_pair_generation_request(
                spec=spec,
                source_context=context,
                form_a_item_id=spec["form_a_item"],
                form_b_item_id=spec["form_b_item"],
                form_a_target_answer=target_answer_for(spec["pair_id"], "甲卷"),
                form_b_target_answer=target_answer_for(spec["pair_id"], "乙卷"),
            )
        )
    return pack


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export 20 source-grounded pair-generation requests as JSON."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "output" / "pair_generation_requests.json",
    )
    args = parser.parse_args()

    pack = build_prompt_pack()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(pack)} pair-generation requests to {args.out}")


if __name__ == "__main__":
    main()
