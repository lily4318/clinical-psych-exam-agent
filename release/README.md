# Formal Releases

此資料夾只保存已經由使用者明確核可的正式版本紀錄。

## Current release pointer

跨對話或重新啟動 Agent 時，第一個讀取的檔案是：`release/current_release.yaml`。

它提供目前正式版本、formal manifest、approval record、最新 review manifest、主題與 Word 輸出規則的固定入口。未來正式版本升版時，應更新此 pointer，而不是要求使用者在新對話中重新描述歷史狀態。

## Current formal release

目前正式版本為：`formal-v1.0`

- 正式 manifest：`formal_release_v1.0.yaml`
- 核可紀錄：`approval_record_v1.0.md`
- 來源審閱版：`review-v0.2`
- 核可日期：2026-10-16
- 核可範圍：甲卷 P01–P20、乙卷 P01–P20
- `approved_by_user=true`
- `quality_status=已核可`

正式 manifest 以 Git blob SHA 鎖定核可當下的五個題組，因此後續 review 區即使出現新版本，也不會改變 `formal-v1.0` 所代表的 40 題內容。

## Versioning rule

任何正式題目內容若需修改，必須：

1. 先建立新的 review 版本；
2. 完成人工審閱；
3. 取得使用者明確核可；
4. 建立新的 formal 版本；
5. 更新 `current_release.yaml` 指向新的正式版本。

不得直接覆寫既有 formal release。

## Word export

正式核可後的 Word 行為依 `agent/word_export_policy.md`：若使用者已要求 Word 則直接輸出；若尚未要求，Agent 必須主動詢問一次。預設套件為甲卷、乙卷、答案與解析三個 `.docx`。
