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


def test_all_four_identical_options_fail_closed_after_bounded_retry(tmp_path):
    """Regression for real Ollama P06-B distinct=1/4, without clinical fixtures."""
    blueprint = load_domain_blueprint()
    evidence = {
        source_id: {
            "url": source["url"], "retrieved_at": "2026-11-23",
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
        options = {letter: f"合成選項{letter}" for letter in "ABCD"}
        if slot["form"] == "乙卷":
            options = {letter: "完全相同的合成選項" for letter in "ABCD"}
        return {"item": {
            "stem": f"{slot['form']} 合成測試題幹，並非臨床題。",
            "options": options,
            "correct_answer": slot["target_answer_position"],
            "rationale": {key: "合成測試解析" for key in ("correct", "A", "B", "C", "D")},
            "sources": [source_id],
        }}

    with pytest.raises(ValueError, match="distinct=1/4"):
        generate_child_parallel_docx(
            model, evidence, tmp_path, items_per_form=1, split_pair_inference=True,
        )
    assert len(calls) == 3  # 甲一次、乙一次、乙有限重生一次
    assert calls[-1]["retry_reason"] == "duplicate_answer_options"
    assert calls[-1]["form"]["form"] == "乙卷"
    assert not list(tmp_path.glob("*.docx"))


def test_rationale_contradiction_retries_once_then_fails_closed(tmp_path):
    """P05-B regression: identical substantive reasons cannot become a DOCX."""
    blueprint = load_domain_blueprint()
    evidence = {
        source_id: {
            "url": source["url"], "retrieved_at": "2026-11-23",
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
        rationale = {
            "correct": "合成正解理由，僅用於程式測試。",
            "A": "正確：合成甲選項理由，僅用於程式測試。",
            "B": "錯誤：合成乙選項理由，僅用於程式測試。",
            "C": "錯誤：合成丙選項理由，僅用於程式測試。",
            "D": "錯誤：合成丁選項理由，僅用於程式測試。",
        }
        if slot["form"] == "乙卷":
            correct = slot["target_answer_position"]
            wrong = next(letter for letter in "ABCD" if letter != correct)
            rationale[correct] = "正確：這是完全相同且足夠長度的合成實質判斷理由。"
            rationale[wrong] = "錯誤：這是完全相同且足夠長度的合成實質判斷理由。"
        return {"item": {
            "stem": f"{slot['form']} 合成情境，僅用於程式回歸。",
            "options": {letter: f"合成選項{letter}" for letter in "ABCD"},
            "correct_answer": slot["target_answer_position"],
            "rationale": rationale,
            "sources": [source_id],
        }}

    with pytest.raises(ValueError, match="Rationale contradiction"):
        generate_child_parallel_docx(
            model, evidence, tmp_path, items_per_form=1, split_pair_inference=True,
        )
    assert len(calls) == 3
    assert calls[-1]["retry_reason"] == "rationale_contradiction"
    assert calls[-1]["form"]["form"] == "乙卷"
    assert "重新推導" in calls[-1]["task"]
    assert not list(tmp_path.glob("*.docx"))


def test_combined_duplicate_and_rationale_error_uses_one_bounded_retry(tmp_path):
    """Both defects must be reported together, then fail closed if still present."""
    blueprint = load_domain_blueprint()
    evidence = {
        source_id: {
            "url": source["url"], "retrieved_at": "2026-11-23",
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
        correct = slot["target_answer_position"]
        wrong = next(letter for letter in "ABCD" if letter != correct)
        rationale = {
            "correct": "合成正解理由，僅供程式測試。",
            **{letter: f"合成選項{letter}的獨立判斷理由。" for letter in "ABCD"},
        }
        options = {letter: f"合成選項{letter}" for letter in "ABCD"}
        if slot["form"] == "乙卷":
            options = {letter: "四項完全相同的合成選項" for letter in "ABCD"}
            rationale[correct] = "正確：完全相同且足夠長度的合成實質判斷理由。"
            rationale[wrong] = "錯誤：完全相同且足夠長度的合成實質判斷理由。"
        return {"item": {
            "stem": f"{slot['form']} 合成測試情境，非臨床題。",
            "options": options,
            "correct_answer": correct,
            "rationale": rationale,
            "sources": [source_id],
        }}

    with pytest.raises(ValueError):
        generate_child_parallel_docx(
            model, evidence, tmp_path, items_per_form=1, split_pair_inference=True,
        )
    assert len(calls) == 3
    assert calls[-1]["form"]["form"] == "乙卷"
    assert calls[-1]["retry_reason"] == "duplicate_answer_options"
    assert "前次正確與錯誤選項使用相同實質理由" in calls[-1]["task"]
    assert "前次輸出的四個選項出現重複" in calls[-1]["task"]
    assert not list(tmp_path.glob("*.docx"))
