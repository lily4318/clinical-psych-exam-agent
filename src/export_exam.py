from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def exam_markdown(exam: dict[str, Any]) -> str:
    lines = [f"# 臨床心理師模擬測驗｜{exam['form']}", "", f"版本：{exam['version']}", ""]
    for number, item in enumerate(exam["items"], start=1):
        lines.append(f"## {number}. {item['stem']}")
        for letter in "ABCD":
            lines.append(f"- ({letter}) {item['options'][letter]}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def answer_key_markdown(exam: dict[str, Any]) -> str:
    lines = [f"# {exam['form']}｜答案與解析", ""]
    for number, item in enumerate(exam["items"], start=1):
        lines.extend(
            [
                f"## {number}. {item['correct_answer']}",
                f"- 配對：{item['pair_id']}",
                f"- 考點：{item['category']}｜{item['subtopic']}",
                f"- 難度／認知：{item['difficulty']}／{item['cognitive_level']}",
                f"- 正解解析：{item['rationale']['correct']}",
                f"- A：{item['rationale']['A']}",
                f"- B：{item['rationale']['B']}",
                f"- C：{item['rationale']['C']}",
                f"- D：{item['rationale']['D']}",
                f"- 來源：{', '.join(item['sources'])}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def export_exam(exam: dict[str, Any], out_dir: str | Path) -> dict[str, Path]:
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    slug = "form_a" if exam["form"] == "甲卷" else "form_b"

    json_path = target / f"{slug}.json"
    exam_md = target / f"{slug}.md"
    answer_md = target / f"{slug}_answers.md"

    json_path.write_text(json.dumps(exam, ensure_ascii=False, indent=2), encoding="utf-8")
    exam_md.write_text(exam_markdown(exam), encoding="utf-8")
    answer_md.write_text(answer_key_markdown(exam), encoding="utf-8")
    return {"json": json_path, "exam": exam_md, "answers": answer_md}


def main() -> None:
    parser = argparse.ArgumentParser(description="Export one exam JSON to Markdown.")
    parser.add_argument("exam_json", type=Path)
    parser.add_argument("--out", type=Path, default=Path("output"))
    args = parser.parse_args()

    exam = json.loads(args.exam_json.read_text(encoding="utf-8"))
    paths = export_exam(exam, args.out)
    for kind, path in paths.items():
        print(f"{kind}: {path}")


if __name__ == "__main__":
    main()
