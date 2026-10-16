from src.load_blueprint import (
    load_blueprint,
    load_pair_source_requirements,
    load_parallel_blueprint,
)


def test_blueprint_totals_match_20_items():
    blueprint = load_blueprint()
    assert blueprint["forms"]["items_per_form"] == 20
    assert sum(v["items_per_form"] for v in blueprint["categories"].values()) == 20
    assert blueprint["form_level_targets"]["difficulty"] == {
        "basic": 2,
        "medium": 11,
        "advanced": 7,
    }
    assert blueprint["form_level_targets"]["cognition"] == {
        "memory": 2,
        "understanding": 8,
        "application": 7,
        "integration": 3,
    }


def test_parallel_blueprint_has_p01_to_p20():
    rows = load_parallel_blueprint()
    assert [row["pair_id"] for row in rows] == [f"P{i:02d}" for i in range(1, 21)]


def test_pair_source_requirements_cover_p01_to_p20():
    rules = load_pair_source_requirements()
    assert list(rules) == [f"P{i:02d}" for i in range(1, 21)]
    assert rules["P08"]["require_all"] == ["SAMHSA-TIP35"]
    assert rules["P13"]["require_all"] == ["APA-DSM5-SUD-CHANGES"]
    assert set(rules["P17"]["require_all"]) == {
        "PUBMED-DELAY-DISCOUNT-2011",
        "NIDA-ADDICTION-SCIENCE",
    }
