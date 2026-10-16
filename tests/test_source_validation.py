from src.generate_exam import _validate_against_spec


def _valid_item() -> dict:
    return {
        "item_id": "甲08",
        "form": "甲卷",
        "pair_id": "P08",
        "stem": "測試用 MI 題幹",
        "options": {"A": "a", "B": "b", "C": "c", "D": "d"},
        "correct_answer": "C",
        "category": "C",
        "subtopic": "MI精神、改變語句與治療者反應",
        "difficulty": "中等",
        "cognitive_level": "理解",
        "rationale": {
            "correct": "測試",
            "A": "測試",
            "B": "測試",
            "C": "測試",
            "D": "測試",
        },
        "sources": ["111-Q18", "NIAAA-MATCH-CBT"],
        "quality_status": "草稿",
    }


def test_missing_pair_required_source_is_rejected():
    spec = {
        "pair_id": "P08",
        "form_a_item": "甲08",
        "form_b_item": "乙08",
        "category": "C",
        "core_topic": "MI精神、改變語句與治療者反應",
        "difficulty": "中等",
        "cognitive_level": "理解",
    }
    errors = _validate_against_spec(
        _valid_item(),
        spec,
        "甲卷",
        {"111-Q18", "NIAAA-MATCH-CBT", "SAMHSA-TIP35"},
        allowed_source_ids={"111-Q18", "NIAAA-MATCH-CBT", "SAMHSA-TIP35"},
        historical_source_ids={"111-Q18"},
        knowledge_source_ids={"NIAAA-MATCH-CBT", "SAMHSA-TIP35"},
        required_all_source_ids={"SAMHSA-TIP35"},
    )
    assert any("SAMHSA-TIP35" in error for error in errors)
