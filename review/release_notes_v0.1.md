# Review Release v0.1

日期：2026-10-16  
狀態：待複核  
使用者最終核可：否

## 版本內容

此版本是第一個完整涵蓋 P01–P20 的甲乙卷人工審閱 release。唯一組卷入口為 `review/release_manifest_v0.1.yaml`。

包含批次：

- P01–P04：`pilot_p01_p04_v0.2.json`
- P05–P08：`pilot_p05_p08_v0.2.json`
- P09–P12：`pilot_p09_p12_v0.2.json`
- P13–P16：`pilot_p13_p16_v0.2.json`
- P17–P20：`pilot_p17_p20_v0.2.json`

## 預期全卷藍圖

每卷 20 題：A4／B3／C2／D4／E4／F3。  
難度：基礎2／中等11／進階7。  
認知層次：記憶2／理解8／應用7／整合3。  
答案位置：A、B、C、D 各 5 題。

## Reviewer 修訂原則

1. 甲乙卷同 pair 必須測相同學習目標、同難度、同認知層次，但不能只換人名、物質或數字。
2. 中等以上題目優先使用臨床情境或功能判斷，而不是單純名詞辨識。
3. 進階／整合題至少兩個干擾選項應包含部分正確概念；錯誤點應落在資訊整合不足、順序、適用時機或漏掉關鍵歷程。
4. 正解不得因明顯較長、較專業或包含最多細節而形成作答線索。
5. 每題至少引用一個歷屆考點與一個權威知識來源；pair-specific 核心來源由 `config/pair_source_requirements.yaml` 強制。
6. DSM、MI、CBT/RP、藥理、生理心理與臺灣政策內容若來源不足，不能以模型記憶補造。

## 本輪重要修訂

- P02：甲乙卷統一回到 mesolimbic dopamine reward pathway 的相同學習目標。
- P04：將明顯荒謬的 CBT 干擾選項改為部分合理但不完整的臨床介入。
- P05：補入 SAMHSA primary／secondary／tertiary prevention 定義來源。
- P07：改為不同物質的耐受／戒斷情境，以符合平行卷規格。
- P09：由關鍵字辨識改為判斷 lapse 後全盤失敗歸因與 AVE 歷程。
- P10：改為同時含風險與保護因素的混合個案，不再使用全對／全錯因素清單。
- P11：干擾選項均含部分多層次預防成分。
- P15、P16：提升高階 MI 與共病整合題的干擾選項品質。
- P18、P20：正解不再是唯一『超長、超完整』選項，其他選項也包含部分合理系統／RP 元素。

## 組卷與驗證

```bash
clinical-psych-review-build
```

或：

```bash
python -m src.assemble_review_exam
```

組卷器會先重新驗證題號、答案位置、藍圖分布、來源與平行卷規格，通過後才輸出完整甲乙卷與檢核報告至 `output/review-v0.1/`。

## CI 狀態

GitHub Actions 目前在此 private repository 會於建立 job 前回傳 `startup_failure`。為避免每次 push 產生無意義的失敗紀錄，自動 push trigger 已暫停，只保留手動 `workflow_dispatch`。此狀態不代表 pytest 已在 GitHub runner 上通過；待帳號／repository Actions 執行設定排除後，再恢復自動 CI。

## 核可規則

此 release 即使所有程式檢核通過，也只能維持 `待複核`。只有使用者明確逐卷或整體核可後，才能建立 `approved_by_user=true` 的正式版本。
