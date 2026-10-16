# Human Review Drafts

此資料夾保存需要人工審閱、且具有版本價值的試產題與 reviewer 紀錄；不代表使用者已核可的正式考卷。

## Canonical review release

目前完整 P01–P20 審閱版由 `release_manifest_v0.1.yaml` 定義。組卷時只能依 manifest 指定的批次，不得自行混用舊版 v0.1／v0.2 檔案。

目前 manifest 使用：

- `pilot_p01_p04_v0.2.json`
- `pilot_p05_p08_v0.2.json`
- `pilot_p09_p12_v0.2.json`
- `pilot_p13_p16_v0.2.json`
- `pilot_p17_p20_v0.2.json`

執行：

```bash
clinical-psych-review-build
```

或：

```bash
python -m src.assemble_review_exam
```

組卷器會重新檢查 P01–P20、題數、A–F 類別、難度、認知層次、答案位置、歷屆來源、pair-specific 核心權威來源與甲乙卷平行結構。任一硬性檢核失敗時，不輸出完整審閱卷。

## 規則

- 所有 review 檔案在使用者明確核可前必須維持 `approved_by_user=false`。
- `待複核` 只代表已經過 Agent reviewer 修訂，不等於 `已核可`。
- 不得因程式檢核通過而自動改成 `已核可`。
- 完整 20+20 題的組卷產物放在 `output/`，由 `.gitignore` 排除，不直接 commit。
- 題目需檢查內容正確性、干擾選項品質、國考風格、甲乙卷等值性與來源充分性。
- 進階／整合題至少兩個干擾選項應包含部分合理概念，錯誤點宜落在資訊整合不足、順序、適用時機或漏掉核心歷程，而非明顯荒謬。
- 只有使用者人工確認後，才能建立正式核可版本。
