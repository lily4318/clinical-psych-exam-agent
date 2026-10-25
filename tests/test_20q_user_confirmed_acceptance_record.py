"""Keep the 20-question user confirmation distinct from independent clinical validation."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TRIAL_20 = ROOT / "docs" / "evals" / "2026-10-25-chatgpt-default-20q-coldstart.yaml"
TRIAL_10 = ROOT / "docs" / "evals" / "2026-10-22-chatgpt-10q-coldstart.yaml"


def _read(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_twenty_question_trial_is_separate_from_ten_question_trial():
    twenty, ten = _read(TRIAL_20), _read(TRIAL_10)
    assert twenty["trial_id"] != ten["trial_id"]
    assert twenty["conversation_title"] == ten["conversation_title"] == "製作模擬考卷 DOCX"
    assert twenty["user_reported_items_per_form"] == {"form_a": 20, "form_b": 20}
    assert twenty["user_reported_items_total"] == 40
    assert ten["requested_items_per_form"] == 10
    assert twenty["trial_scenario"].startswith("T2")


def test_twenty_question_trial_user_confirmation_is_preserved_with_denominators():
    trial = _read(TRIAL_20)
    assert trial["user_visible_acceptance"]["criteria_checked"] == 9
    assert trial["user_visible_acceptance"]["criteria_passed"] == 9
    checks = trial["user_visible_acceptance"]["checks"]
    assert len(checks) == 9
    assert len({entry["id"] for entry in checks}) == 9
    assert all(entry["result"] == "pass_user_confirmed" for entry in checks)
    assert all(
        trial["first_final_response"][field] == "confirmed_by_user"
        for field in (
            "form_a_docx_link_present", "form_b_docx_link_present",
            "form_a_downloaded_and_opened", "form_b_downloaded_and_opened",
        )
    )
    assert trial["metrics"]["first_turn_downloadable_20_item_trials"] == {
        "passed": 1, "observed": 1
    }


def test_user_visible_success_does_not_imply_independent_file_or_expert_acceptance():
    trial = _read(TRIAL_20)
    gates = trial["acceptance_gates"]
    assert gates["G3_user_visible_document_structure"] == "pass_user_confirmed"
    assert gates["G3_independent_programmatic_docx_check"].startswith("not_tested")
    assert gates["G4_first_turn_two_downloadable_files"] == "pass_user_confirmed"
    assert gates["G5_independent_expert_clinical_accuracy_and_source_support"] == "not_tested"
    assert gates["G5_parallel_psychometric_equivalence"] == "not_tested"
    assert gates["full_independent_quality_acceptance"] == "not_yet_verified"
    assert trial["artifacts"]["actual_docx_bytes_accessible_for_independent_audit"] is False
    assert trial["repository_sha_actually_read_by_trial"] == "unknown"
    assert trial["metrics"]["independent_G3_docx_checks"]["attempted"] == 0
    assert trial["metrics"]["independently_expert_reviewed_new_items"]["attempted"] == 0


def test_cold_start_acceptance_ledger_links_to_both_distinct_trials():
    text = (ROOT / "docs" / "CROSS_PLATFORM_ACCEPTANCE.md").read_text(encoding="utf-8")
    assert TRIAL_10.name in text
    assert TRIAL_20.name in text
    assert "9/9" in text
    assert "G5" in text
    assert "不同事件" in text
