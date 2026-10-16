from src.load_exam_history import select_latest_exam_years


def test_select_latest_exam_years_uses_latest_five_distinct_years():
    rows = [
        {"year": "110", "item_id": "110-A"},
        {"year": "111", "item_id": "111-A"},
        {"year": "112", "item_id": "112-A"},
        {"year": "113", "item_id": "113-A"},
        {"year": "114", "item_id": "114-A"},
        {"year": "115", "item_id": "115-A"},
        {"year": "115", "item_id": "115-B"},
    ]

    selected = select_latest_exam_years(rows, count=5)

    assert {row["year"] for row in selected} == {"111", "112", "113", "114", "115"}
    assert [row["item_id"] for row in selected] == [
        "111-A",
        "112-A",
        "113-A",
        "114-A",
        "115-A",
        "115-B",
    ]


def test_select_latest_exam_years_shifts_when_new_year_is_added():
    rows = [{"year": str(year), "item_id": f"{year}-A"} for year in range(110, 117)]

    selected = select_latest_exam_years(rows, count=5)

    assert {row["year"] for row in selected} == {"112", "113", "114", "115", "116"}


def test_select_latest_exam_years_uses_all_when_fewer_than_five_exist():
    rows = [
        {"year": "114", "item_id": "114-A"},
        {"year": "115", "item_id": "115-A"},
    ]

    assert select_latest_exam_years(rows, count=5) == rows
