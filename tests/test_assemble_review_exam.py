from src.assemble_review_exam import assemble_review_release, load_review_manifest


def test_review_manifest_covers_all_pairs_once():
    manifest = load_review_manifest()
    assert manifest["expected_pairs"] == [f"P{i:02d}" for i in range(1, 21)]
    assert len(manifest["batches"]) == 5
    assert manifest["approved_by_user"] is False


def test_canonical_review_release_passes_full_validation():
    form_a, form_b, report = assemble_review_release()
    assert report["ok"], report["errors"]
    assert len(form_a["items"]) == 20
    assert len(form_b["items"]) == 20
    assert form_a["approved_by_user"] is False
    assert form_b["approved_by_user"] is False
    assert [item["pair_id"] for item in form_a["items"]] == [f"P{i:02d}" for i in range(1, 21)]
    assert [item["pair_id"] for item in form_b["items"]] == [f"P{i:02d}" for i in range(1, 21)]
    assert report["metrics"]["甲卷"]["metrics"]["category"] == {
        "A": 4,
        "E": 4,
        "B": 3,
        "D": 4,
        "F": 3,
        "C": 2,
    }
    assert report["metrics"]["甲卷"]["metrics"]["difficulty"] == {
        "基礎": 2,
        "中等": 11,
        "進階": 7,
    }
    assert report["metrics"]["甲卷"]["metrics"]["cognition"] == {
        "記憶": 2,
        "應用": 7,
        "理解": 8,
        "整合": 3,
    }
    assert report["metrics"]["甲卷"]["metrics"]["answers"] == {
        "A": 5,
        "C": 5,
        "B": 5,
        "D": 5,
    }
    assert report["metrics"]["乙卷"]["metrics"]["answers"] == {
        "B": 5,
        "D": 5,
        "A": 5,
        "C": 5,
    }
