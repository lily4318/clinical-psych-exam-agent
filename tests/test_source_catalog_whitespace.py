"""Regression: whitespace in source IDs must not hide available bibliography."""
from docx import Document

from src.export_docx import export_exam_docx


def test_source_catalog_lookup_uses_canonical_trimmed_source_id(tmp_path):
    exam = {
        "form": "甲卷",
        "version": "catalog-whitespace-regression",
        "domain_id": "child_adolescent",
        "items": [{
            "stem": "測試題幹（非真實臨床試題）",
            "options": {letter: f"測試選項 {letter}" for letter in "ABCD"},
            "correct_answer": "A",
            "rationale": {
                "correct": "測試用正解說明。",
                **{letter: f"{letter} 選項測試解析。" for letter in "ABCD"},
            },
            "sources": ["  TEST-SOURCE-001  "],
        }],
        "source_catalog": {
            "TEST-SOURCE-001": {
                "title": "可追溯來源（合成測試）",
                "url": "https://example.org/synthetic-source",
            },
        },
    }

    path = export_exam_docx(exam, tmp_path)
    paragraphs = [p.text for p in Document(path).paragraphs]
    assert "第 1 題：TEST-SOURCE-001" in paragraphs
    assert "[TEST-SOURCE-001] 可追溯來源（合成測試）" in paragraphs
    assert "https://example.org/synthetic-source" in paragraphs
