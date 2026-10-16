# Human Review Drafts

此資料夾保存需要人工審閱、且具有版本價值的試產題與 reviewer 紀錄；review 檔本身保留建立時的審閱狀態，不直接改寫成正式考卷。

## Formal approval status

`review-v0.2` 已於 2026-10-16 由使用者以明確語句「正式核可 review-v0.2 甲卷與乙卷」完成核可。

正式核可紀錄不覆寫本資料夾的歷史 review metadata，而是獨立建立於：

- `release/formal_release_v1.0.yaml`
- `release/approval_record_v1.0.md`

正式 manifest 以 Git blob SHA 鎖定核可當下的五個題組內容，因此未來 review 區若再新增或修改版本，不會改變 `formal-v1.0`。

## Canonical review release

完整 P01–P20 歷史審閱版由 `release_manifest_v0.2.yaml` 定義。`release_manifest_v0.1.yaml` 保留作為更早的歷史版本。組審閱卷時只能依 canonical review manifest 指定的批次，不得自行混用舊稿。

review-v0.2 使用：

- `pilot_p01_p04_v0.2.json`
- `pilot_p05_p08_v0.3.json`
- `pilot_p09_p12_v0.3.json`
- `pilot_p13_p16_v0.2.json`
- `pilot_p17_p20_v0.3.json`

執行：

```bash
clinical-psych-review-build
```

或：

```bash
python -m src.assemble_review_exam
```

組卷器會重新檢查 P01–P20、題數、A–F 類別、難度、認知層次、答案位置、歷屆來源、pair-specific 核心權威來源與甲乙卷平行結構。任一硬性檢核失敗時，不輸出完整審閱卷。

## Reviewer 規則

- review 檔案保留人工審閱歷史；正式核可另以 `release/` 下的 formal manifest 記錄。
- `待複核` 只代表已經過 Agent reviewer 修訂，不等於 `已核可`。
- 不得因程式檢核通過而自動改成 `已核可`。
- 完整 20+20 題的組卷產物放在 `output/`，由 `.gitignore` 排除，不直接 commit。
- 題目需檢查內容正確性、干擾選項品質、國考風格、甲乙卷等值性與來源充分性。
- 進階／整合題至少兩個干擾選項應包含部分合理概念，錯誤點宜落在資訊整合不足、順序、適用時機或漏掉核心歷程，而非明顯荒謬。
- 中等題允許存在「中等偏易」的核心概念錨點；不要為了提高表面難度，把全部中等題都改成多步驟整合題。
- 考生視角審查需刻意忽略解析與來源，只看題幹和選項是否有雙答案、正解長度線索、關鍵字送分或實際難度低於藍圖的問題。
- 只有使用者人工確認後，才能建立正式核可版本；正式版建立後不得無版本號直接覆寫。
