"""Positive bounded-repair acceptance: synthetic fixtures, no clinical content."""
from src.child_exam_pipeline import generate_child_parallel_docx
from src.domain_blueprints import load_domain_blueprint
from src.verify_external_delivery import verify_pair


def test_rationale_repair_can_recover_and_deliver_both_docs(tmp_path):
    """The one allowed retry must permit a valid repaired item, not just fail closed."""
    blueprint = load_domain_blueprint()
    evidence = {
        sid: {
            "url": source["url"],
            "retrieved_at": "2026-11-24",
            "passage": "Synthetic provenance-only fixture, not clinical evidence. " * 3,
        }
        for sid, source in blueprint["sources"].items()
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
            **{letter: f"合成選項{letter}具有各自不同的判斷理由。" for letter in "ABCD"},
        }
        if slot["form"] == "乙卷" and not request.get("retry_reason"):
            rationale[correct] = "正確：這段合成實質理由長度足夠，內容完全一致。"
            rationale[wrong] = "錯誤：這段合成實質理由長度足夠，內容完全一致。"
        return {"item": {
            "stem": f"{slot['form']} 獨立合成題幹，非臨床題。",
            "options": {letter: f"合成選項{letter}" for letter in "ABCD"},
            "correct_answer": correct,
            "rationale": rationale,
            "sources": [source_id],
        }}

    paths = generate_child_parallel_docx(
        model, evidence, tmp_path, items_per_form=1, split_pair_inference=True,
    )
    assert len(calls) == 3
    assert calls[2]["retry_reason"] == "rationale_contradiction"
    assert calls[2]["form"]["form"] == "乙卷"
    assert verify_pair(paths["form_a"], paths["form_b"], 1)["ok"]
    assert len(list(tmp_path.glob("*.docx"))) == 2
