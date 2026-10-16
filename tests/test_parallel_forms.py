from src.check_parallel_forms import check_parallel_forms
from src.generate_exam import generate_parallel_drafts
from src.load_blueprint import load_blueprint, load_parallel_blueprint
from src.load_exam_history import (
    known_source_ids,
    load_answer_source_catalog,
    load_historical_index,
    load_knowledge_sources,
    load_official_sources,
)


def test_stub_pipeline_is_structurally_equivalent():
    a, b = generate_parallel_drafts()
    report = check_parallel_forms(
        a,
        b,
        load_blueprint(),
        load_parallel_blueprint(),
        known_source_ids(
            load_historical_index(),
            load_official_sources(),
            load_answer_source_catalog(),
            load_knowledge_sources(),
        ),
    )
    assert report["ok"], report["errors"]
    assert report["forms"]["甲卷"]["metrics"]["answers"] == {
        "A": 5,
        "C": 5,
        "B": 5,
        "D": 5,
    }
    assert report["forms"]["乙卷"]["metrics"]["answers"] == {
        "B": 5,
        "D": 5,
        "A": 5,
        "C": 5,
    }
