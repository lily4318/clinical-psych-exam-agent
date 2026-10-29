"""Prepare auditable child-guideline excerpts independently of local Ollama.

This is a free, source-only operation. It never generates questions, invokes a
model, approves clinical claims, or modifies the immutable formal release.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from .child_exam_pipeline import _preflight_evidence
from .child_source_fetch import fetch_official_guidance_evidence
from .domain_blueprints import build_child_pair_specs, load_domain_blueprint


def prepare_child_evidence(out: str | Path, *, items_per_form: int = 20) -> Path:
    """Fetch official excerpts once and publish an exclusive reusable JSON file.

    The output is accepted by child_exam_pipeline --evidence. Presence and
    provenance checks are not independent verification of clinical assertions.
    On a source failure or conflicting output path, no JSON is published.
    """
    if isinstance(items_per_form, bool) or not isinstance(items_per_form, int) or items_per_form < 1:
        raise ValueError("items_per_form must be a positive integer.")

    target = Path(out)
    if os.path.lexists(target):
        raise FileExistsError(f"Refusing to overwrite existing evidence: {target}")

    blueprint = load_domain_blueprint()
    specs = build_child_pair_specs(items_per_form, blueprint=blueprint)
    required_ids = {sid for spec in specs for sid in spec["source_ids"]}
    evidence = fetch_official_guidance_evidence(blueprint["sources"], required_ids)

    # The same preflight as actual generation: every planned pair needs an
    # original passage and the exact allowlisted source URL.
    _preflight_evidence(specs, blueprint["sources"], evidence)
    if set(evidence) != required_ids:
        raise ValueError("Source fetch returned an unexpected source ID set.")

    target.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".child-evidence-stage-", dir=target.parent) as stage:
        staged = Path(stage) / "evidence.json"
        staged.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        # Exclusive publication prevents a concurrent writer from being
        # overwritten between the initial preflight and final publication.
        os.link(staged, target)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch allowlisted child clinical guidance to JSON; no Ollama or paid API."
    )
    parser.add_argument("--out", type=Path, required=True, help="New evidence JSON path")
    parser.add_argument("--items", type=int, default=20, help="Items in each future exam form")
    args = parser.parse_args()
    saved = prepare_child_evidence(args.out, items_per_form=args.items)
    print(f"Official excerpt evidence saved: {saved}")
    print("Source presence checked; clinical semantic support is NOT expert-verified.")


if __name__ == "__main__":
    main()
