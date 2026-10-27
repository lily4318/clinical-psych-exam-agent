"""Offline transport regression for the manual draft-release shell step.

The fake gh executable simulates GitHub CLI transport only. It is NOT evidence
of a real GitHub Release, clinical correctness, or user-downloadable files.
"""
import os
from pathlib import Path
import subprocess

import pytest
import yaml


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/manual_child_draft_release.yml"

FAKE_GH = r'''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import shutil
import sys

args = sys.argv[1:]
root = Path(os.environ["GH_FAKE_DIR"])
root.mkdir(parents=True, exist_ok=True)
with (root / "commands.txt").open("a", encoding="utf-8") as log:
    log.write(" ".join(args) + "\n")
if args[:2] == ["release", "create"]:
    assets = root / "assets"
    assets.mkdir(exist_ok=True)
    for arg in args[3:]:
        src = Path(arg)
        if src.suffix == ".docx":
            shutil.copyfile(src, assets / src.name)
    print("https://github.com/lily4318/clinical-psych-exam-agent/releases/tag/test")
elif args[:2] == ["release", "view"]:
    assets = root / "assets"
    data = {
        "isDraft": True,
        "isPrerelease": True,
        "url": "https://github.com/lily4318/clinical-psych-exam-agent/releases/tag/test",
        "assets": [
            {"name": p.name, "size": p.stat().st_size, "url": "https://example.invalid/" + p.name}
            for p in sorted(assets.glob("*.docx"))
        ],
    }
    print(json.dumps(data))
elif args[:2] == ["release", "download"]:
    destination = Path(args[args.index("--dir") + 1])
    destination.mkdir(parents=True, exist_ok=True)
    for src in (root / "assets").glob("*.docx"):
        shutil.copyfile(src, destination / src.name)
    if os.environ.get("GH_FAKE_CORRUPT") == "1":
        with next(destination.glob("form_b_*.docx")).open("ab") as f:
            f.write(b"corrupt")
elif args[:2] == ["release", "delete"]:
    shutil.rmtree(root / "assets", ignore_errors=True)
else:
    sys.exit("Unexpected fake gh command: " + " ".join(args))
'''


@pytest.mark.parametrize("corrupt", [False, True])
def test_draft_release_shell_retrieves_identical_bytes_or_cleans_up(tmp_path, corrupt):
    """Run the actual YAML publish script with fake transport, not a substring test."""
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    step = next(
        s for s in workflow["jobs"]["publish-draft"]["steps"]
        if s.get("name", "").startswith("Publish only verified files")
    )
    script = step["run"]
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(FAKE_GH, encoding="utf-8")
    gh.chmod(0o755)
    output = tmp_path / "output"
    output.mkdir()
    for form in ("a", "b"):
        (output / f"form_{form}_child-unverified-v0.1.docx").write_bytes(
            (form * 100).encode("ascii")
        )
    fake = tmp_path / "fake"
    summary = tmp_path / "summary.md"
    env = {
        **os.environ,
        "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
        "OUT_DIR": str(output),
        "ITEMS": "3",
        "GITHUB_RUN_ID": "123456",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_SHA": "a" * 40,
        "GITHUB_STEP_SUMMARY": str(summary),
        "GH_FAKE_DIR": str(fake),
        "GH_FAKE_CORRUPT": "1" if corrupt else "0",
        "GH_TOKEN": "offline-test-placeholder",
    }
    completed = subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", script],
        env=env, text=True, capture_output=True, timeout=30,
    )
    commands = (fake / "commands.txt").read_text(encoding="utf-8")
    assert "release create " in commands
    assert "release view " in commands
    assert "release download " in commands
    if corrupt:
        assert completed.returncode != 0
        assert "release delete " in commands
        assert not (fake / "assets").exists()
    else:
        assert completed.returncode == 0, completed.stderr + completed.stdout
        assert "release delete " not in commands
        assert "UNVERIFIED" in summary.read_text(encoding="utf-8")
        assert len(list((fake / "assets").glob("*.docx"))) == 2
