"""Portable AI-Agent discovery checks; never tests clinical correctness."""

import re
from pathlib import Path

import pytest
import yaml

from src.domain_blueprints import build_child_pair_specs

ROOT = Path(__file__).resolve().parents[1]
MAIN_SKILL = ROOT / ".agents" / "skills" / "clinical-psych-exam" / "SKILL.md"
CLAUDE_SKILL = ROOT / ".claude" / "skills" / "clinical-psych-exam" / "SKILL.md"


def _read_skill(path: Path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.S)
    assert match, f"{path} must have Agent Skills YAML frontmatter"
    meta = yaml.safe_load(match.group(1))
    assert isinstance(meta, dict)
    return meta, match.group(2)


@pytest.mark.parametrize("path", [MAIN_SKILL, CLAUDE_SKILL])
def test_skills_have_valid_standard_frontmatter(path):
    meta, instructions = _read_skill(path)
    assert meta["name"] == path.parent.name == "clinical-psych-exam"
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", meta["name"])
    assert 1 <= len(meta["name"]) <= 64
    assert isinstance(meta.get("description"), str)
    assert 1 <= len(meta["description"]) <= 1024
    assert instructions.strip()
    assert "START_HERE.md" in instructions
    assert "Word" in instructions


def test_agents_entry_points_do_not_override_canonical_rules():
    root_agent = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    _, skill = _read_skill(MAIN_SKILL)
    _, claude_adapter = _read_skill(CLAUDE_SKILL)
    for name in (
        "START_HERE.md",
        "config/simulation_policy.yaml",
        "release/current_release.yaml",
        "agent/system_prompt.md",
        "docs/CROSS_PLATFORM_ACCEPTANCE.md",
    ):
        assert name in root_agent
        assert name in skill
    assert ".agents/skills/clinical-psych-exam/SKILL.md" in claude_adapter
    assert "formal-v1.0" in root_agent
    assert "formal-v1.0" in skill
    assert "Stub" in root_agent or "mocked" in root_agent
    assert "Word 尚未交付" in root_agent
    assert "Word 尚未交付" in skill
    assert "Word 尚未交付" in claude_adapter


def test_repo_url_skill_requires_real_first_reply_attachments():
    _, skill = _read_skill(MAIN_SKILL)
    assert "https://github.com/lily4318/clinical-psych-exam-agent" in skill
    assert "下載甲卷 Word" in skill
    assert "下載乙卷 Word" in skill
    assert "first final answer" in skill
    assert "src.verify_external_delivery" in skill
    assert "G4" in skill and "G5" in skill


@pytest.mark.parametrize("items", [3, 10, 20])
def test_user_selected_question_counts_are_supported_in_child_planner(items):
    slots = build_child_pair_specs(items)
    assert len(slots) == items
    assert [p["pair_id"] for p in slots] == [
        f"P{number:02d}" for number in range(1, items + 1)
    ]
    assert all(p["source_status"] == "candidate_requires_item_level_verification" for p in slots)


def test_acceptance_document_distinguishes_verified_and_unverified():
    doc = (ROOT / "docs" / "CROSS_PLATFORM_ACCEPTANCE.md").read_text(encoding="utf-8")
    assert "2026-10-22" in doc
    assert "1/1" in doc
    assert "0/1" in doc
    assert "使用者確認" in doc
    assert "尚未在此取得該次原始檔案做獨立 G3" in doc
    assert "Claude、Gemini" in doc


def test_discovery_is_not_misrepresented_as_external_platform_success():
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    _, claude_skill = _read_skill(CLAUDE_SKILL)
    assert "does not install a model" in agents
    assert "does **not** guarantee automatic skill installation" in claude_skill
