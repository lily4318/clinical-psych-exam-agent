from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


def _safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip(".-") or "draft"


def _validate_exam(exam: dict[str, Any], *, include_answers: bool) -> None:
    if exam.get("form") not in {"甲卷", "乙卷"}:
        raise ValueError("Expected a 甲卷 or 乙卷 exam.")
    items = exam.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("Exam must contain a non-empty items list.")
    for number, item in enumerate(items, start=1):
        if not isinstance(item, dict) or not str(item.get("stem", "")).strip():
            raise ValueError(f"Item {number} requires a question stem.")
        options = item.get("options")
        if not isinstance(options, dict) or any(
            not str(options.get(letter, "")).strip() for letter in "ABCD"
        ):
            raise ValueError(f"Item {number} requires non-empty A-D options.")
        if include_answers:
            answer = item.get("correct_answer")
            if not isinstance(answer, str) or answer not in {"A", "B", "C", "D"}:
                raise ValueError(f"Item {number} requires one valid answer letter.")
            rationale = item.get("rationale")
            if not isinstance(rationale, dict) or not str(
                rationale.get("correct", "")
            ).strip():
                raise ValueError(f"Item {number} requires a correct-answer rationale.")


def export_exam_docx(
    exam: dict[str, Any],
    out_dir: str | Path,
    *,
    include_answers: bool = True,
) -> Path:
    """Export an exam to real Word; optionally append its key and rationales."""
    _validate_exam(exam, include_answers=include_answers)
    destination = Path(out_dir)
    destination.mkdir(parents=True, exist_ok=True)

    document = Document()
    section = document.sections[0]
    section.top_margin = Cm(2.2)
    section.bottom_margin = Cm(2.2)
    section.left_margin = Cm(2.3)
    section.right_margin = Cm(2.3)

    normal = document.styles["Normal"]
    normal.font.name = "Microsoft JhengHei"
    normal.font.size = Pt(10.5)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft JhengHei")

    title = document.add_heading(f"臨床心理師模擬測驗｜{exam['form']}", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    version = str(exam.get("version") or "draft")
    document.add_paragraph(f"版本：{version}　題數：{len(exam['items'])}")
    if exam.get("approved_by_user") is not True:
        document.add_paragraph("自動產生之模擬測驗；未標示為使用者正式核可版本。")

    for number, item in enumerate(exam["items"], start=1):
        document.add_heading(f"{number}. {item['stem']}", level=2)
        for letter in "ABCD":
            document.add_paragraph(f"({letter}) {item['options'][letter]}")

    if include_answers:
        document.add_page_break()
        document.add_heading(f"{exam['form']}｜答案與解析", 0)
        document.add_paragraph("此處為教師／自學參考，考生作答時請勿提前閱讀。")
        answer_table = document.add_table(rows=1, cols=2)
        answer_table.style = "Table Grid"
        answer_table.rows[0].cells[0].text = "題號"
        answer_table.rows[0].cells[1].text = "答案"
        for number, item in enumerate(exam["items"], start=1):
            cells = answer_table.add_row().cells
            cells[0].text = str(number)
            cells[1].text = item["correct_answer"]

        for number, item in enumerate(exam["items"], start=1):
            document.add_heading(f"{number}. {item['correct_answer']}", level=2)
            rationale = item["rationale"]
            document.add_paragraph(f"正解解析：{rationale['correct']}")
            for letter in "ABCD":
                detail = str(rationale.get(letter, "")).strip()
                if detail:
                    document.add_paragraph(f"{letter}：{detail}")
            source_ids = item.get("sources") or []
            if source_ids:
                document.add_paragraph("來源 ID：" + ", ".join(map(str, source_ids)))

    slug = "form_a" if exam["form"] == "甲卷" else "form_b"
    name = f"{slug}_{_safe_slug(version)}.docx"
    path = destination / name
    document.save(path)
    return path


def export_parallel_docx(
    form_a: dict[str, Any],
    form_b: dict[str, Any],
    out_dir: str | Path,
    *,
    include_answers: bool = True,
) -> dict[str, Path]:
    """Export exactly two Word files; no formal-release approval is implied."""
    _validate_exam(form_a, include_answers=include_answers)
    _validate_exam(form_b, include_answers=include_answers)
    if form_a["form"] != "甲卷" or form_b["form"] != "乙卷":
        raise ValueError("Expected form_a=甲卷 and form_b=乙卷.")
    if len(form_a["items"]) != len(form_b["items"]):
        raise ValueError("Parallel forms must have the same item count.")
    if str(form_a.get("version") or "draft") != str(form_b.get("version") or "draft"):
        raise ValueError("Parallel forms must use the same version.")
    for number, (item_a, item_b) in enumerate(
        zip(form_a["items"], form_b["items"]), start=1
    ):
        if item_a.get("pair_id") != item_b.get("pair_id"):
            raise ValueError(f"Pair ID mismatch at item {number}.")

    return {
        "form_a": export_exam_docx(form_a, out_dir, include_answers=include_answers),
        "form_b": export_exam_docx(form_b, out_dir, include_answers=include_answers),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export an existing validated parallel pair to two Word documents."
    )
    parser.add_argument("form_a", type=Path, help="甲卷 JSON")
    parser.add_argument("form_b", type=Path, help="乙卷 JSON")
    parser.add_argument("--out", type=Path, default=Path("output/docx"))
    parser.add_argument("--hide-answers", action="store_true")
    args = parser.parse_args()
    form_a = json.loads(args.form_a.read_text(encoding="utf-8"))
    form_b = json.loads(args.form_b.read_text(encoding="utf-8"))
    paths = export_parallel_docx(
        form_a, form_b, args.out, include_answers=not args.hide_answers
    )
    for name, path in paths.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
