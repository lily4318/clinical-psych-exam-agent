from src.export_exam import export_exam
from src.generate_exam import generate_parallel_drafts


def test_export_writes_json_exam_and_answer_key(tmp_path):
    a, _ = generate_parallel_drafts()
    paths = export_exam(a, tmp_path)
    assert paths["json"].exists()
    assert paths["exam"].exists()
    assert paths["answers"].exists()
    assert "答案與解析" in paths["answers"].read_text(encoding="utf-8")
