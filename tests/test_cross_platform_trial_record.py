"""Regression checks for auditable external AI trials, not model or clinical QA."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs" / "evals" / "2026-10-22-chatgpt-10q-coldstart.yaml"


def read_trial():
    return yaml.safe_load(RECORD.read_text(encoding="utf-8"))


def test_10q_trial_identifies_exact_conversation_and_counts():
    trial = read_trial()
    assert trial["conversation_title"] == "製作模擬考卷 DOCX"
    assert trial["requested_items_per_form"] == 10
    assert trial["generation_claims"]["items_per_form"] == 10
    assert sum(trial["generation_claims"]["blueprint_allocation_each_form"].values()) == 10
    assert trial["repository_main_sha_observed"] != "unknown"


def test_10q_link_presence_is_not_conflated_with_download_success():
    trial = read_trial()
    reply = trial["first_final_response"]
    assert reply["occurred"] is True
    assert set(reply["link_presence"].values()) == {"observed"}
    assert set(reply["actual_download_and_open"].values()) == {"not_yet_confirmed"}
    assert reply["file_bytes_independently_available"] is False
    assert trial["acceptance"]["G4_first_response_two_links_present"] == "observed_pass"
    assert trial["acceptance"]["G4_downloadable_and_openable"] == "unknown"
    assert trial["measures"]["first_response_two_links_present_trials"] == {
        "passed": 1, "total_observed": 1
    }
    assert trial["measures"]["first_response_download_confirmed_trials"] == {
        "passed": 0, "total_verified": 0
    }


def test_10q_clinical_and_structural_quality_remains_unverified():
    trial = read_trial()
    acceptance = trial["acceptance"]
    assert acceptance["G3_docx_structure"].startswith("unverified")
    assert acceptance["G5_independent_clinical_evidence"] == "not_tested"
    assert acceptance["overall_full_acceptance"] == "not_yet_verified"
    assert trial["measures"]["G3_independent_file_checks"]["total_verified"] == 0
    assert trial["measures"]["independently_reviewed_new_items"]["total_verified"] == 0
    assert trial["repository_sha_read_by_test_agent"] == "unknown"
    assert trial["generation_claims"]["applied_native_repo_validator"] == "no_execution_evidence"


def test_public_acceptance_ledger_links_trial_without_upgrading_status():
    doc = (ROOT / "docs" / "CROSS_PLATFORM_ACCEPTANCE.md").read_text(encoding="utf-8")
    assert RECORD.name in doc
    assert "首次連結存在" in doc
    assert "尚未驗證" in doc
    assert "0筆可評分試驗" in doc
