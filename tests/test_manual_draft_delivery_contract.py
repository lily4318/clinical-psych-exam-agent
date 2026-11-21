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


def test_draft_release_requires_explicit_owner_main_dispatch():
    text = _workflow()
    assert "workflow_dispatch:" in text
    assert "github.event_name == 'workflow_dispatch'" in text
    assert "github.actor == 'lily4318'" in text
    assert "github.triggering_actor == 'lily4318'" in text
    assert "github.ref == 'refs/heads/main'" in text
    assert "github.repository == 'lily4318/clinical-psych-exam-agent'" in text
    assert "github.event.repository.private == false" in text
    assert "pull_request:" not in text and "pull_request_target:" not in text


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
