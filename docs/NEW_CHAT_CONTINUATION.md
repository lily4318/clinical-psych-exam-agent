# 新對話接續使用指南

這個 repository 是「臨床心理師考題 Agent」的持久狀態與正式版本來源。換新 ChatGPT 對話時，不需要依賴舊對話記憶，也不需要重新敘述已經寫入 GitHub 的背景。

## 新對話固定啟動語

在新的 ChatGPT 對話直接貼上：

> 請接續我的「臨床心理師考題 Agent」。GitHub repo 是 lily4318/clinical-psych-exam-agent。請先讀 release/current_release.yaml、agent/system_prompt.md、docs/NEW_CHAT_CONTINUATION.md，以及 current_release 指向的 formal/review manifest，再告訴我目前正式版本、進行狀態與可繼續的下一步。不要依賴舊對話記憶，也不要要求我重新敘述已寫入 repo 的背景。

Agent 應先讀 repository，再簡短回報目前正式版本、主題、核可狀態與下一步，之後才能繼續工作。

## 若 GitHub 尚未連線

先在 ChatGPT 連接／重新授權 GitHub connector，再貼上上述固定啟動語。不要以聊天記憶取代 repository 版本資料。

## 目前正式版本的使用方式

目前正式入口由 `release/current_release.yaml` 指向。若只需要重新輸出目前正式考卷，可直接說：

> 請依 current formal release 輸出 Word。

若要修改既有題目、增加新主題、建立新甲乙卷或調整藍圖，必須保留既有 formal release，不得覆寫；應建立新的 review 版本，完成人工審閱後，再由使用者明確核可並升為新的 formal 版本。

## 核可規則

只有使用者明確說出「核可」、「正式核可」或「批准」，並指向特定版本、卷別或題組，才算正式核可。

例如：

- `正式核可 review-v0.3 甲卷與乙卷`
- `核可 review-v0.3 甲卷`

「可以」、「差不多可以」、「看起來沒問題」、「繼續」等只代表繼續工作或正向回饋，不得自動升為正式版本。

## 正式核可後的 Word 行為

- 若使用者在同一工作流程中已經要求 Word，正式核可後應直接產出 Word，不再重問。
- 若使用者尚未要求 Word，正式核可並完成 formal release 後，Agent 必須主動詢問一次是否輸出 Word。
- 預設 Word 套件為三個檔案：甲卷（不含答案）、乙卷（不含答案）、答案與解析。
- Word 應完全依 manifest 鎖定的題組輸出，並在檔名標示版本號。

詳細輸出規則見 `agent/word_export_policy.md`。
