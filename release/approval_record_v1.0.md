# Formal Approval Record｜formal-v1.0

狀態：已核可  
`approved_by_user=true`  
`quality_status=已核可`

## 核可事件

- 核可日期：2026-10-16
- 核可語句：`正式核可 review-v0.2 甲卷與乙卷`
- 核可範圍：甲卷 P01–P20、乙卷 P01–P20，共 40 題
- 來源審閱版本：`review-v0.2`
- 正式版本：`formal-v1.0`

## 凍結內容

正式版本由 `release/formal_release_v1.0.yaml` 定義，並以 Git blob SHA 鎖定下列五個題組：

| Pair 範圍 | 檔案 | Blob SHA |
|---|---|---|
| P01–P04 | `review/pilot_p01_p04_v0.2.json` | `aea6be825d2b868a15c9e58383a4265f22e05b87` |
| P05–P08 | `review/pilot_p05_p08_v0.3.json` | `ad0f1f9836d4212577c15b0debadc14e70faee4e` |
| P09–P12 | `review/pilot_p09_p12_v0.3.json` | `ebfe73b3af87b2617ce4eb9f60d5e2423e928bb6` |
| P13–P16 | `review/pilot_p13_p16_v0.2.json` | `14544079e54d341ccf370cdd7dc5b06dd7478f28` |
| P17–P20 | `review/pilot_p17_p20_v0.3.json` | `9e031ba45bceed0ca9047f738f43b3f87fbc1c6c` |

來源 review manifest：`review/release_manifest_v0.2.yaml`，blob SHA `4c7378f8d94e33f449007f8fc604c1c2eca11d9b`。

## 核可前人工審閱摘要

使用者已完成甲乙卷各 20 題的實際作答與考生視角檢視。未發現必須修訂的雙答案、重大題意歧義或不可接受的題型問題。P02 被保留為未來盲測可優先觀察的等值性題組；P12 顯示為真實藥理知識難點，未因單一作答者表現降低難度。

真人實測採先甲後乙，且部分甲卷錯題在乙卷作答前曾提供答案與解析，因此該次 70% vs 85% 的原始分數差異不得視為正式心理計量等值證據。此限制不影響使用者對題目內容與兩份考卷的正式核可。

## 版本治理

1. `review-v0.2` 的原始審閱 manifest、題組與 reviewer 紀錄保留歷史狀態，不覆寫為正式版。
2. `formal-v1.0` 是本次正式核可後的基準版本。
3. 未來若修改任何題幹、選項、答案、解析、來源、難度或認知層次，必須另建新的 review 版本，再經明確核可後升為新的 formal 版本。
4. 不得在不變更正式版本號的情況下替換本次凍結的題組內容。

## CI／自動測試註記

本次正式核可是人工內容核可，不代表 GitHub Actions 或 pytest 已成功執行。Repository 先前的 GitHub Actions 仍有 job 建立前 `startup_failure` 的已知狀態，因此不得將此核可紀錄解讀為自動測試已通過。
