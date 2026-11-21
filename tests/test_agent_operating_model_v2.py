"""Static V2 routing contracts; not evidence of live LLM, clinical validity or DOCX G4."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "exam-evidence-blueprint",
    "exam-compose",
    "exam-docx-delivery",
    "exam-continuous-improvement",
)


def test_v2_skills_exist_with_frontmatter():
    for name in SKILLS:
        f = ROOT / ".agents" / "skills" / name / "SKILL.md"
        assert f.is_file(), name
        text = f.read_text(encoding="utf-8")
        assert text.startswith("---\n") and f"name: {name}" in text


def test_v2_router_points_to_skills_and_canonical_release():
    router = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    portable = (ROOT / ".agents/skills/clinical-psych-exam/SKILL.md").read_text(encoding="utf-8")
    for name in SKILLS:
        assert f".agents/skills/{name}/SKILL.md" in router
        assert name in portable
    assert "START_HERE.md" in router
    assert "release/current_release.yaml" in router


def test_v2_architecture_has_protection_and_delivery_contract():
    architecture = (ROOT / "docs/AGENT_ARCHITECTURE_V2.md").read_text(encoding="utf-8")
    taskbook = (ROOT / "docs/EXAM_TASKBOOK.md").read_text(encoding="utf-8")
    state = (ROOT / "docs/AGENT_RUN_STATE.md").read_text(encoding="utf-8")
    lessons = (ROOT / "docs/AGENT_LESSONS.md").read_text(encoding="utf-8")
    assert "formal-v1.0" in architecture
    assert "命題規範與來源依據" in architecture
    assert "G3" in taskbook and "G4" in taskbook
    assert "Word 尚未交付" in taskbook
    assert "40833369315" in state
    assert "正式政策" in lessons
