from src.check_examinee_surface import check_item_surface


def _item(options, correct="D"):
    return {
        "item_id": "測試01",
        "options": options,
        "correct_answer": correct,
    }


def test_warns_when_correct_option_is_much_longer():
    warnings = check_item_surface(
        _item(
            {
                "A": "短選項一",
                "B": "短選項二",
                "C": "短選項三",
                "D": "這是一個明顯比其他三個選項長很多而且包含多個額外限定條件與完整解釋的正確選項，因此可能形成作答線索",
            }
        )
    )
    assert any("length cue" in warning for warning in warnings)


def test_warns_when_distractors_share_absolute_wording_pattern():
    warnings = check_item_surface(
        _item(
            {
                "A": "只要出現此現象就一定成立",
                "B": "所有個案都必然符合這個結論",
                "C": "完全不需要考慮其他資訊",
                "D": "此現象需要和其他臨床資訊一併判斷",
            }
        )
    )
    assert any("absolute wording" in warning for warning in warnings)


def test_balanced_options_can_pass_without_surface_warning():
    warnings = check_item_surface(
        _item(
            {
                "A": "先評估近期症狀與功能變化，再決定後續介入方向",
                "B": "先建立行為時間序列，再比較不同情境下的症狀變化",
                "C": "先檢查主要風險來源，再和個案討論可能的因應方法",
                "D": "先整合現有資訊，再依評估結果選擇最適當的處理策略",
            }
        )
    )
    assert warnings == []
