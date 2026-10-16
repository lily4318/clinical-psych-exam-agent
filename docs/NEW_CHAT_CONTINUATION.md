# 新對話接續使用指南

這個 repository 是「臨床心理師考題 Agent」的持久狀態與正式版本來源。

## 最簡單的使用方式

在任何新對話，只要貼：

> `https://github.com/lily4318/clinical-psych-exam-agent 你的任務`

例如：

> `https://github.com/lily4318/clinical-psych-exam-agent 幫我做兒童版考卷`

> `https://github.com/lily4318/clinical-psych-exam-agent 幫我再出20題`

> `https://github.com/lily4318/clinical-psych-exam-agent 幫我輸出目前正式版Word`

AI 應自行讀取 `START_HERE.md`，再載入 `release/current_release.yaml`、`agent/system_prompt.md` 與任務需要的 manifest／blueprint／題組／來源檔，不得要求使用者重新貼完整啟動說明或舊對話背景。

## 已經在同一個 Agent 對話中

若本對話已經載入本 Agent，之後可只下短指令，例如：

- `幫我做兒童版考卷`
- `改成青少年版`
- `再出20題`
- `檢查甲乙卷是否等值`
- `輸出Word`

Agent 應自動沿用目前狀態。

## 分享給其他老師／研究者

直接把公開 repo 網址給對方即可。最推薦的分享文字只有一行：

> `https://github.com/lily4318/clinical-psych-exam-agent 請依這個Agent幫我做＿＿＿＿`

對方可以把空格換成自己的任務。

公開使用時，本 repo 預設為唯讀範本。如果對方只是使用 Agent，不需要 fork；如果希望長期保存自己的題目、審閱紀錄與正式版本，建議先 Fork 到自己的 GitHub，再改貼自己的 fork 網址。

## 預設行為

- 未指定主題：沿用目前 Agent 主題。
- 未指定題數與卷型：沿用目前藍圖。
- `兒童版` 未指定年齡：預設國小高年級可理解的語言與情境，並在輸出時註明。
- `青少年版`：預設國中至高中情境。
- 若合理預設即可完成，Agent 應直接做，不先用大量澄清問題阻斷工作。

## 核可與 Word

只有明確說出「核可／正式核可／批准」並指向版本、卷別或題組才算正式核可。

正式核可後：

- 若之前已要求 Word，直接產出。
- 若尚未要求 Word，Agent 主動詢問是否輸出 Word。

預設 Word 套件：甲卷、乙卷、答案與解析。

## 儲存來源

GitHub 是唯一持久 source of truth。原 Google Drive 已刪除，不再使用。
