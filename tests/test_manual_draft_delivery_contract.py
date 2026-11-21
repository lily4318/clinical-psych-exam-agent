"""Fail-closed static contract for the owner-only, unverified DOCX draft release.

These tests do not trigger workflow_dispatch, generate questions, or claim G4.
They protect the security and retrievability checks from accidental deletion.
"""
from pathlib import Path

WORKFLOW = (
    Path(__file__).resolve().parents[1]
    / ".github/workflows/manual_child_draft_release.yml"
)


def _workflow() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def _job_guard(text: str) -> str:
    """Read the actual publish-draft job if expression, never comments or docs."""
    import re

    match = re.search(
        r"(?m)^  publish-draft:\\s*\\n    if: (\\$\\{\\{[^\\n]+\\}\\})\\s*$",
        text,
    )
    assert match is not None, "publish-draft must have an active job-level if guard"
    return match.group(1)


def test_draft_release_requires_explicit_owner_main_dispatch():
    text = _workflow()
    assert '"on":\\n  workflow_dispatch:' in text
    guard = _job_guard(text)
    for clause in (
        "github.event_name == 'workflow_dispatch'",
        "github.actor == 'lily4318'",
        "github.triggering_actor == 'lily4318'",
        "github.ref == 'refs/heads/main'",
        "github.repository == 'lily4318/clinical-psych-exam-agent'",
        "github.event.repository.private == false",
    ):
        assert clause in guard, f"Missing active owner-only guard: {clause}"
    assert "pull_request:" not in text and "pull_request_target:" not in text


def test_owner_guard_cannot_be_satisfied_by_comments_only():
    """Regression: moving a guard clause to a comment must fail the contract."""
    import pytest

    original = _workflow()
    guard = _job_guard(original)
    clause = "github.triggering_actor == 'lily4318'"
    assert clause in guard
    weakened = original.replace(
        " && " + clause, "",
        1,
    ) + "\\n# " + clause + "\\n"
    assert clause in weakened
    with pytest.raises(AssertionError):
        assert clause in _job_guard(weakened)


def test_draft_release_is_bounded_and_only_publishes_verified_files():
    text = _workflow()
    assert '[[ "$ITEMS" =~ ^(3|8|20)$ ]]' in text
    assert "python -m src.verify_external_delivery" in text
    assert "steps.verify.outcome == 'success'" in text
    assert "gh release create" in text
    assert "--draft --prerelease" in text
    assert ".assets | length == 2" in text
    assert "gh release download" in text
    assert 'cmp -s "${a[0]}"' in text
    assert 'cmp -s "${b[0]}"' in text
    assert "gh release delete" in text


def test_draft_release_does_not_use_paid_api_or_claim_formal_validation():
    text = _workflow()
    assert "ollama pull qwen2.5:3b" in text
    assert "UNVERIFIED child/adolescent" in text
    assert "NOT formal-v1.0" in text
    assert "not ChatGPT attachments" in text
    assert "clinical/source semantic accuracy" in text
    assert "api.openai.com" not in text
    assert "actions/upload-artifact" not in text
