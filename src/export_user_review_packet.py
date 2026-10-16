from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from .assemble_review_exam import assemble_review_release

ROOT = Path(__file__).resolve().parents[1]


def exam_only_markdown(exam: dict[str, Any]) -> str:
    lines = [
        f"# 臨床心理師模擬測驗｜{exam['form']}｜使用者審閱版",
        "",
        f"版本：{exam['version']}",
        "",
        "> 本檔刻意隱藏正確答案、解析、考點、難度、來源與 pair metadata。請只從考生實際看到的題目判斷品質。",
        "",
    ]
    for number, item in enumerate(exam["items"], start=1):
        lines.append(f"## {number}. {item['stem']}")
        for letter in "ABCD":
            lines.append(f"- ({letter}) {item['options'][letter]}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def review_sheet_markdown(form_a: dict[str, Any], form_b: dict[str, Any]) -> str:
    lines = [
        "# review-v0.2｜使用者逐題審閱表",
        "",
        "請在不先看答案解析的情況下審閱。若某題有問題，可直接記錄題號與原因。",
        "",
        "建議標記：`OK`／`題意不清`／`疑似雙答案`／`太簡單`／`太難`／`不像國考`／`選項有線索`／`需改寫`。",
        "",
        "## 甲卷",
        "",
        "| 題號 | 判定 | 備註 |",
        "|---:|---|---|",
    ]
    for index, _ in enumerate(form_a["items"], start=1):
        lines.append(f"| {index} |  |  |")

    lines.extend(
        [
            "",
            "## 乙卷",
            "",
            "| 題號 | 判定 | 備註 |",
            "|---:|---|---|",
        ]
    )
    for index, _ in enumerate(form_b["items"], start=1):
        lines.append(f"| {index} |  |  |")

    lines.extend(
        [
            "",
            "## 整卷觀察",
            "",
            "- 甲卷整體難度：",
            "- 乙卷整體難度：",
            "- 兩卷是否感覺等值：",
            "- 哪些題目最像國考：",
            "- 哪些題目最需要修改：",
            "- 其他意見：",
            "",
            "## 核可狀態",
            "",
            "本表填寫完成不代表自動核可。只有使用者明確表示『核可 review-v0.2 甲卷／乙卷／整份 review-v0.2』才可改變核可狀態。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def export_user_review_packet(out_dir: str | Path) -> dict[str, Path]:
    form_a, form_b, report = assemble_review_release()
    if not report["ok"]:
        raise ValueError("Canonical review release failed validation; review packet not exported.")

    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    paths = {
        "form_a": target / "form_a_user_review.md",
        "form_b": target / "form_b_user_review.md",
        "review_sheet": target / "user_review_sheet.md",
    }
    paths["form_a"].write_text(exam_only_markdown(form_a), encoding="utf-8")
    paths["form_b"].write_text(exam_only_markdown(form_b), encoding="utf-8")
    paths["review_sheet"].write_text(
        review_sheet_markdown(form_a, form_b), encoding="utf-8"
    )
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export answer-hidden review-v0.2 exams and a user review sheet."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "output" / "review-v0.2" / "user-review",
    )
    args = parser.parse_args()
    paths = export_user_review_packet(args.out)
    for label, path in paths.items():
        print(f"{label}: {path}")


if __name__ == "__main__":
    main()
