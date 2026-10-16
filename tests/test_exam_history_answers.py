from src.load_exam_history import (
    load_answer_source_catalog,
    load_historical_index,
    load_knowledge_sources,
    load_official_answer_keys,
    merge_history_with_answers,
)


def test_all_historical_items_have_answer_status():
    history = load_historical_index()
    answers = load_official_answer_keys()
    merged = merge_history_with_answers(history, answers)

    assert len(history) == 74
    assert len(answers) == 74
    assert len(merged) == 74

    choice_items = [row for row in merged if row["source_item"].startswith("Q")]
    essay_items = [row for row in merged if row["source_item"].startswith("E")]

    assert len(choice_items) == 71
    assert len(essay_items) == 3
    assert all(row["official_answer"] in {"A", "B", "C", "D"} for row in choice_items)
    assert all(row["answer_status"] == "final_official" for row in choice_items)
    assert all(row["official_answer"] == "" for row in essay_items)
    assert all(row["answer_status"] == "essay_no_abcd_key" for row in essay_items)


def test_answer_and_knowledge_catalogs_have_unique_source_ids():
    answer_sources = load_answer_source_catalog()
    knowledge_sources = load_knowledge_sources()

    answer_ids = [row["source_id"] for row in answer_sources]
    knowledge_ids = [row["source_id"] for row in knowledge_sources]

    assert len(answer_ids) == len(set(answer_ids))
    assert len(knowledge_ids) == len(set(knowledge_ids))
    assert "MOEX-111-M" in answer_ids
    assert "SAMHSA-TIP35" in knowledge_ids
    assert "NIAAA-MATCH-CBT" in knowledge_ids
