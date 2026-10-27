"""Static security/contract checks for optional manual draft Word delivery.

This test does not contact GitHub or assert that a release was published.
"""
from pathlib import Path

import yaml


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/manual_child_draft_release.yml"


def test_manual_draft_delivery_is_fail_closed_and_uses_no_actions_artifacts():
    raw = WORKFLOW.read_text(encoding="utf-8")
    workflow = yaml.safe_load(raw)

    assert set(workflow["on"]) == {"workflow_dispatch"}
    assert workflow["permissions"] == {"contents": "write"}
    assert set(workflow["on"]["workflow_dispatch"]["inputs"]["items"]["options"]) == {"3", "8", "20"}
    job = workflow["jobs"]["publish-draft"]
    assert job["runs-on"] == "ubuntu-latest"
    assert job["timeout-minutes"] <= 360
    assert "github.event_name == 'workflow_dispatch'" in job["if"]
    assert "github.repository == 'lily4318/clinical-psych-exam-agent'" in job["if"]

    steps = job["steps"]
    verify_idx = next(i for i, step in enumerate(steps) if step.get("id") == "verify")
    publish_idx = next(i for i, step in enumerate(steps) if "gh release create" in step.get("run", ""))
    assert verify_idx < publish_idx
    verify = steps[verify_idx]["run"]
    publish = steps[publish_idx]["run"]
    assert "src.verify_external_delivery" in verify
    assert "--items \"$ITEMS\"" in verify
    assert "sha256sum" in verify
    assert "--draft --prerelease" in publish
    assert "steps.verify.outcome == 'success'" in steps[publish_idx]["if"]
    assert "gh release view" in publish
    assert "isDraft == true" in publish
    assert "isPrerelease == true" in publish
    assert "gh release delete" in publish
    assert "upload-artifact" not in raw
    assert "pull_request_target:" not in raw
    assert "OPENAI_API_KEY" not in raw
    assert "ollama pull qwen2.5:3b" in raw
