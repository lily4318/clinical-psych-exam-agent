"""Regression for user-reported clinical time reversal and copy-pasted rationales.

Synthetic development fixtures only, not formal items or an independent expert test.
"""
from src.child_exam_pipeline import _check_item, _request, _single_form_request

SPEC = {
    "pair_id": "P02", "category": "TEST", "core_topic": "deadline",
    "difficulty": "medium", "cognitive_level": "apply",
    "equivalence_note": "同考點但不同臨床情境的合成測試配對",
    "form_a_item": "P02", "form_b_item": "P02",
}
EXPECTED = {"item_id": "P02", "form": "甲卷", "target_answer_position": "B"}
EXCERPT = (
    "1.5.1 Start the autism diagnostic assessment within 3 months "
    "of the referral to the autism team."
)
CONTEXT = [{"source_id": "NICE-CG128", "excerpt": EXCERPT}]


def _item():
    return {
        "item_id": "P02", "form": "甲卷", "pair_id": "P02",
        "category": "TEST", "subtopic": "deadline", "difficulty": "medium",
        "cognitive_level": "apply", "quality_status": "草稿",
        "stem": "轉介至自閉症團隊後，應在何時開始診斷評估？",
        "options": {
            "A": "至少在轉介滿3個月後開始",
            "B": "在轉介後3個月內開始",
            "C": "至少在轉介滿6個月後開始",
            "D": "等到學校學年結束再開始",
        },
        "correct_answer": "B",
        "rationale": {
            "correct": "官方指引要求在轉介後3個月內開始。",
            "A": "錯誤，至少要等3個月後才開始與指引矛盾。",
            "B": "正確，NICE指南要求在轉介後3個月內開始診斷評估。",
            "C": "錯誤，6個月後超出指引的開始期限。",
            "D": "錯誤，不能依學年終點取代開始期限。",
        },
        "sources": ["NICE-CG128"],
    }


def _errors(item, context=CONTEXT):
    return _check_item(item, SPEC, EXPECTED, {"NICE-CG128"}, context)


def test_known_within_to_at_least_later_reversal_is_rejected():
    item = _item()
    item["rationale"]["B"] = (
        "正確，因為NICE指南建議在孩子被推薦給自閉症團隊後，"
        "至少在3個月後開始自閉症診斷評估。"
    )
    errors = _errors(item)
    assert any("Temporal source contradiction" in error for error in errors)


def test_same_clinical_reason_for_right_and_wrong_is_rejected():
    item = _item()
    item["rationale"]["A"] = (
        "不正確，因為NICE指南要求轉介到自閉症團隊後3個月內開始診斷評估。"
    )
    item["rationale"]["B"] = (
        "正確，因為NICE指南要求轉介到自閉症團隊後3個月內開始診斷評估。"
    )
    assert any("Rationale contradiction" in error for error in _errors(item))


def test_legitimate_source_grounded_deadline_has_no_new_failures():
    assert _errors(_item()) == []


def test_shared_wrong_option_reason_is_allowed_for_later_word_consolidation():
    item = _item()
    common = "不正確，因為選項未遵守轉介後3個月內必須開始的期限。"
    for letter in "ACD":
        item["rationale"][letter] = common
    assert _errors(item) == []


def test_explicitly_negating_wrong_deadline_is_not_flagged_as_positive_claim():
    item = _item()
    item["rationale"]["B"] = (
        "正確，因為指引是3個月內開始，並非至少在3個月後才開始。"
    )
    assert _errors(item) == []


def test_malformed_source_list_returns_error_not_type_error():
    item = _item()
    item["sources"] = [{"wrong": "type"}]
    errors = _errors(item)
    assert any("Sources" in error for error in errors)


def test_real_model_request_contains_semantic_polarity_and_discrimination_rules():
    request = _request(SPEC, CONTEXT, 2)
    rules = "\n".join(request["constraints"])
    assert "within 3 months=3個月內" in rules
    assert "相同理由" in rules
    single = _single_form_request(request, "form_a")
    assert "within 3 months表示3個月內" in single["task"]
    assert "相同實質理由" in single["task"]
