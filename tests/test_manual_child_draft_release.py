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
    # The write-capable token must not reach pip, downloaded sources or Ollama.
    assert "GH_TOKEN" not in job.get("env", {})
    assert job["timeout-minutes"] <= 360
    assert "github.event_name == 'workflow_dispatch'" in job["if"]
    assert "github.repository == 'lily4318/clinical-psych-exam-agent'" in job["if"]
    # github.actor is the original actor; triggering_actor catches non-owner reruns.
    assert "github.actor == 'lily4318'" in job["if"]
    assert "github.triggering_actor == 'lily4318'" in job["if"]
    assert "github.ref == 'refs/heads/main'" in job["if"]

    steps = job["steps"]
    verify_idx = next(i for i, step in enumerate(steps) if step.get("id") == "verify")
    publish_idx = next(i for i, step in enumerate(steps) if "gh release create" in step.get("run", ""))
    assert verify_idx < publish_idx
    checkout = next(step for step in steps if step.get("uses", "").startswith("actions/checkout@"))
    assert checkout["with"]["persist-credentials"] is False
    assert steps[publish_idx]["env"]["GH_TOKEN"] == "${{ github.token }}"
    assert all("GH_TOKEN" not in step.get("env", {}) for i, step in enumerate(steps) if i != publish_idx)
    verify = steps[verify_idx]["run"]
    publish = steps[publish_idx]["run"]
    assert "src.verify_external_delivery" in verify
    assert "--items \"$ITEMS\"" in verify
    assert "sha256sum" in verify
    assert "--draft --prerelease" in publish
    assert "steps.verify.outcome == 'success'" in steps[publish_idx]["if"]
    assert "gh release view" in publish
    # Verify remotely retrievable bytes, not just names/sizes from release metadata.
    assert "gh release download" in publish
    assert publish.count("cmp -s") == 2
    assert publish.index("gh release view") < publish.index("gh release download")
    assert publish.index("gh release download") < publish.index("cmp -s")
    assert "trap cleanup_on_failure EXIT" in publish
    assert "isDraft == true" in publish
    assert "isPrerelease == true" in publish
    assert "gh release delete" in publish
    assert "upload-artifact" not in raw
    assert "runner.temp" not in raw  # runner context is invalid in job-level env
    assert "pull_request_target:" not in raw
    assert "OPENAI_API_KEY" not in raw
    assert "ollama pull qwen2.5:3b" in raw
