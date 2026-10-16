from src.check_parallel_forms import check_parallel_forms
from src.generate_exam import generate_parallel_pairs
from src.load_blueprint import load_blueprint, load_parallel_blueprint
from src.load_exam_history import (
    known_source_ids,
    load_answer_source_catalog,
    load_historical_index,
    load_knowledge_sources,
    load_official_sources,
)
from src.provider import CallbackPairQuestionProvider


def _fake_pair_callback(request: dict) -> dict:
    spec = request["pair_spec"]

    def make_item(form_spec: dict, scenario: str) -> dict:
        answer = form_spec["target_answer_position"]
        options = {
            letter: f"{scenario} 選項 {letter}"
            for letter in "ABCD"
        }
        return {
            "item_id": form_spec["item_id"],
            "form": form_spec["form"],
            "pair_id": spec["pair_id"],
            "stem": f"{scenario}：測量 {spec['core_topic']} 的測試題幹。",
            "options": options,
            "correct_answer": answer,
            "category": spec["category"],
            "subtopic": spec["core_topic"],
            "difficulty": spec["difficulty"],
            "cognitive_level": spec["cognitive_level"],
            "rationale": {
                "correct": "測試用正解說明",
                "A": "測試用 A 說明",
                "B": "測試用 B 說明",
                "C": "測試用 C 說明",
                "D": "測試用 D 說明",
            },
            "quality_status": "草稿",
        }

    return {
        "pair_id": spec["pair_id"],
        "form_a": make_item(request["forms"][0], "甲卷不同情境"),
        "form_b": make_item(request["forms"][1], "乙卷不同情境"),
        "equivalence_notes": "測試用等值說明",
    }


def test_pair_provider_generates_two_valid_twenty_item_forms():
    provider = CallbackPairQuestionProvider(_fake_pair_callback)
    a, b = generate_parallel_pairs(provider, version="test")

    known = known_source_ids(
        load_historical_index(),
        load_official_sources(),
        load_answer_source_catalog(),
        load_knowledge_sources(),
    )
    report = check_parallel_forms(
        a,
        b,
        load_blueprint(),
        load_parallel_blueprint(),
        known,
    )

    assert len(a["items"]) == 20
    assert len(b["items"]) == 20
    assert report["ok"], report["errors"]
