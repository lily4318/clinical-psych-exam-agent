"""Catch option duplicates before spending further local model inference.

Synthetic fixtures only. No clinical claims, paid API, or formal-release changes.
"""
import pytest

from src.child_exam_pipeline import _check_item, generate_child_parallel_docx
from src.domain_blueprints import load_domain_blueprint
from src.verify_external_delivery import verify_pair


@pytest.mark.parametrize(("first", "second"), [
    ("合成Ａ", "合成A"),       # NFKC fullwidth equivalence
    ("合 成選項", "合成選項"),  # Internal whitespace
    ("合成　A", "合成 A"),     # Fullwidth space
])
def test_child_model_gate_matches_docx_option_normalization(first, second):
    """Previously _check_item accepted these, but the exporter rejected them."""
    spec = {
        "pair_id": "P01", "category": "TEST", "core_topic": "synthetic",
        "difficulty": "medium", "cognitive_level": "apply",
    }
    expected = {"item_id": "P01", "form": "甲卷", "target_answer_position": "A"}
    item = {
        **{key: value for key, value in [
            ("item_id", "P01"), ("form", "甲卷"), ("pair_id", "P01"),
            ("category", "TEST"), ("subtopic", "synthetic"),
            ("difficulty", "medium"), ("cognitive_level", "apply"),
            ("quality_status", "草稿"), ("correct_answer", "A"),
        ]},
        "stem": "純程式合成題幹，不是臨床試題。",
        "options": {"A": first, "B": second, "C": "不同選項C", "D": "不同選項D"},
        "rationale": {key: "合成解析文字" for key in ("correct", "A", "B", "C", "D")},
        "sources": ["SYNTHETIC"],
    }
    errors = _check_item(item, spec, expected, {"SYNTHETIC"})
    assert len(errors) == 1
    assert "distinct=3/4" in errors[0]


def test_split_inference_repairs_nfkc_duplicate_before_word_export(tmp_path):
    """One bounded regeneration, not a late exporter failure after all model calls."""
    blueprint = load_domain_blueprint()
    evidence = {
        source_id: {
            "url": source["url"], "retrieved_at": "2026-10-29",
            "passage": "Synthetic provenance-only test passage. " * 4,
        }
        for source_id, source in blueprint["sources"].items()
        if source["kind"] == "clinical_guideline"
    }
    calls = []

    def model(request):
        calls.append(request)
        slot = request["form"]
        source_id = request["source_context"][0]["source_id"]
        options = {"A": "合成A", "B": "合成B", "C": "合成C", "D": "合成D"}
        if slot["form"] == "甲卷" and not request.get("retry_reason"):
            options["B"] = "合成Ａ"
        return {"item": {
            "stem": f"{slot['form']} 合成程式測試情境，不是真實臨床題。",
            "options": options,
            "correct_answer": slot["target_answer_position"],
            "rationale": {key: "合成測試解析" for key in ("correct", "A", "B", "C", "D")},
            "sources": [source_id],
        }}

    paths = generate_child_parallel_docx(
        model, evidence, tmp_path, items_per_form=1, split_pair_inference=True,
    )
    assert len(calls) == 3
    assert calls[1]["retry_reason"] == "duplicate_answer_options"
    assert calls[1]["form"]["form"] == "甲卷"
    assert verify_pair(paths["form_a"], paths["form_b"], 1)["ok"]
    assert len(list(tmp_path.glob("*.docx"))) == 2
