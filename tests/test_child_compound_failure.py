"""Regression for the real P05 compound structural failure (no clinical claims)."""

import pytest

from src.child_exam_pipeline import generate_child_parallel_docx
from src.domain_blueprints import load_domain_blueprint


def test_fifth_pair_duplicate_options_and_unknown_source_fail_closed(tmp_path):
    """P05 failure must not publish P01-P04 as a partial pair of Word files."""
    blueprint = load_domain_blueprint()
    evidence = {
        source_id: {
            "url": source["url"],
            "passage": "Synthetic evidence for structural regression only. " * 5,
            "retrieved_at": "2026-10-26T00:00:00Z",
        }
        for source_id, source in blueprint["sources"].items()
        if source["kind"] == "clinical_guideline"
    }
    calls = []

    def model(request):
        calls.append((request["pair_spec"]["pair_id"], request["form"]["form"]))
        spec, slot = request["pair_spec"], request["form"]
        options = {
            "A": "Synthetic option alpha",
            "B": "Synthetic option beta",
            "C": "Synthetic option gamma",
            "D": "Synthetic option delta",
        }
        sources = [request["source_context"][0]["source_id"]]
        if spec["pair_id"] == "P05":
            options["B"] = options["A"]
            options["D"] = options["A"]
            sources = ["UNKNOWN-SOURCE"]
        return {"item": {
            "stem": f"Synthetic {spec['pair_id']} {slot['form']} structural test only.",
            "options": options,
            "correct_answer": slot["target_answer_position"],
            "rationale": {
                "correct": "Synthetic correct-answer explanation.",
                "A": "Synthetic explanation A.",
                "B": "Synthetic explanation B.",
                "C": "Synthetic explanation C.",
                "D": "Synthetic explanation D.",
            },
            "sources": sources,
        }}

    with pytest.raises(ValueError) as caught:
        generate_child_parallel_docx(
            model, evidence, tmp_path, items_per_form=8,
            split_pair_inference=True,
        )
    message = str(caught.value)
    assert "P05 form_a" in message
    assert "distinct=2/4" in message
    assert "Sources must cite unique IDs" in message
    assert len(calls) == 9
    assert calls[-1] == ("P05", "甲卷")
    assert not list(tmp_path.glob("*.docx"))
