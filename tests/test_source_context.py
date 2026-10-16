from src.load_blueprint import load_parallel_blueprint
from src.load_exam_history import (
    load_historical_index,
    load_knowledge_sources,
)
from src.source_context import build_source_context


def _pair(pair_id: str) -> dict[str, str]:
    return next(row for row in load_parallel_blueprint() if row["pair_id"] == pair_id)


def test_mi_pair_selects_mi_authority_and_history():
    context = build_source_context(
        _pair("P08"),
        load_historical_index(),
        load_knowledge_sources(),
    )
    ids = {row["source_id"] for row in context}
    assert "SAMHSA-TIP35" in ids
    assert any(source_id.startswith(("110-", "111-", "112-", "113-", "114-", "115-")) for source_id in ids)


def test_cbt_pair_selects_cbt_manual():
    context = build_source_context(
        _pair("P20"),
        load_historical_index(),
        load_knowledge_sources(),
    )
    ids = {row["source_id"] for row in context}
    assert "NIAAA-MATCH-CBT" in ids


def test_neuro_pair_selects_nida_science_resource():
    context = build_source_context(
        _pair("P17"),
        load_historical_index(),
        load_knowledge_sources(),
    )
    ids = {row["source_id"] for row in context}
    assert "NIDA-ADDICTION-SCIENCE" in ids
