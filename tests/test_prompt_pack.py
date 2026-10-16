from src.export_prompt_pack import build_prompt_pack


def test_prompt_pack_contains_20_parallel_pair_requests():
    pack = build_prompt_pack()
    assert len(pack) == 20
    assert [row["pair_spec"]["pair_id"] for row in pack] == [f"P{i:02d}" for i in range(1, 21)]


def test_prompt_pack_controls_answer_positions_and_sources():
    pack = build_prompt_pack()
    p03 = next(row for row in pack if row["pair_spec"]["pair_id"] == "P03")
    p05 = next(row for row in pack if row["pair_spec"]["pair_id"] == "P05")

    assert p03["forms"][0]["target_answer_position"] in "ABCD"
    assert p03["forms"][1]["target_answer_position"] in "ABCD"
    assert "PUBMED-TLFB-2000" in {row["source_id"] for row in p03["source_context"]}
    assert "MOJ-ANTIDRUG-STRATEGY3" in {row["source_id"] for row in p05["source_context"]}
