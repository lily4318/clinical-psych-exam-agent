from src.assemble_review_exam import assemble_review_release
from src.export_user_review_packet import exam_only_markdown, review_sheet_markdown


def test_exam_only_markdown_hides_answers_and_rationales():
    form_a, _, report = assemble_review_release()
    assert report["ok"], report["errors"]
    text = exam_only_markdown(form_a)
    assert "使用者審閱版" in text
    assert "正確答案" not in text
    assert "correct_answer" not in text
    assert "解析" in text  # appears only in the notice saying it is hidden
    assert "來源：" not in text
    assert "P01" not in text


def test_review_sheet_has_20_rows_per_form_and_no_auto_approval():
    form_a, form_b, report = assemble_review_release()
    assert report["ok"], report["errors"]
    text = review_sheet_markdown(form_a, form_b)
    assert text.count("| 20 |  |  |") == 2
    assert "填寫完成不代表自動核可" in text
    assert "核可 review-v0.2" in text
