"""Reject non-string question/option payloads before writing either DOCX.

Synthetic test data only; no approved exam or clinical question content.
"""

import pytest

from src.export_docx import export_parallel_docx


def _form(label):
    return {
        "form": label,
        "version": "synthetic-nonstring-gate",
        "items": [{
            "pair_id": "P01",
            "stem": f"{label} 的合成題幹（非臨床試題）",
            "options": {key: f"{label} 測試選項 {key}" for key in "ABCD"},
            "correct_answer": "A",
            "rationale": {
                "correct": "合成測試正解說明",
                **{key: f"合成測試 {key} 解析" for key in "ABCD"},
            },
            "sources": ["SYNTHETIC-SOURCE-001"],
        }],
    }


@pytest.mark.parametrize("invalid_stem", [None, 0, True, ["not", "a", "string"]])
def test_parallel_export_rejects_nonstring_stem_before_writes(tmp_path, invalid_stem):
    a, b = _form("甲卷"), _form("乙卷")
    b["items"][0]["stem"] = invalid_stem
    with pytest.raises(ValueError, match="requires a question stem"):
        export_parallel_docx(a, b, tmp_path)
    assert not list(tmp_path.glob("*.docx"))


@pytest.mark.parametrize("invalid_option", [None, 0, False, ["not a string"]])
def test_parallel_export_rejects_nonstring_option_before_writes(tmp_path, invalid_option):
    a, b = _form("甲卷"), _form("乙卷")
    b["items"][0]["options"]["C"] = invalid_option
    with pytest.raises(ValueError, match="requires non-empty A-D options"):
        export_parallel_docx(a, b, tmp_path)
    assert not list(tmp_path.glob("*.docx"))


def test_parallel_export_rejects_missing_option_before_writes(tmp_path):
    a, b = _form("甲卷"), _form("乙卷")
    b["items"][0]["options"].pop("C")
    with pytest.raises(ValueError, match="requires non-empty A-D options"):
        export_parallel_docx(a, b, tmp_path)
    assert not list(tmp_path.glob("*.docx"))
