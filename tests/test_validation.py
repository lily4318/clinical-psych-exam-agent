from src.validate_item import validate_item


def valid_item():
    return {
        "item_id": "甲01",
        "form": "甲卷",
        "pair_id": "P01",
        "stem": "測試題幹",
        "options": {"A": "一", "B": "二", "C": "三", "D": "四"},
        "correct_answer": "A",
        "category": "A",
        "subtopic": "SUD",
        "difficulty": "基礎",
        "cognitive_level": "記憶",
        "rationale": {
            "correct": "正解",
            "A": "A",
            "B": "B",
            "C": "C",
            "D": "D",
        },
        "sources": ["110-Q26"],
        "quality_status": "草稿",
    }


def test_valid_item_passes():
    assert validate_item(valid_item(), {"110-Q26"}) == []


def test_duplicate_option_is_rejected():
    item = valid_item()
    item["options"]["B"] = item["options"]["A"]
    errors = validate_item(item, {"110-Q26"})
    assert any("unique" in error for error in errors)


def test_unknown_source_is_rejected():
    item = valid_item()
    errors = validate_item(item, {"OTHER"})
    assert any("Unknown source IDs" in error for error in errors)
