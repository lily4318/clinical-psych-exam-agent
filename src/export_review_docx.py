from __future__ import annotations

import argparse
from pathlib import Path

from .assemble_review_exam import assemble_review_release
from .export_docx import export_parallel_docx


def export_review_docx(
    output_dir: str | Path,
    *,
    include_answers: bool = True,
) -> dict[str, Path]:
    """Build two Word files from the existing validated review manifest.

    This is for the existing review-v0.2 topic, not for generating new
    childhood psychology questions or approving a formal release.
    """
    form_a, form_b, report = assemble_review_release()
    if not report["ok"]:
        raise ValueError(
            "Review release did not pass full validation: "
            + "; ".join(report["errors"])
        )
    return export_parallel_docx(
        form_a, form_b, output_dir, include_answers=include_answers
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export the existing validated review release as two Word files."
    )
    parser.add_argument("--out", type=Path, default=Path("output/review-docx"))
    parser.add_argument("--hide-answers", action="store_true")
    args = parser.parse_args()
    paths = export_review_docx(
        args.out, include_answers=not args.hide_answers
    )
    for label, path in paths.items():
        print(f"{label}: {path}")


if __name__ == "__main__":
    main()
