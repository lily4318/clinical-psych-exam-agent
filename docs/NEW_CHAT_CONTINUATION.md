# 新對話接續使用指南

這個 repository 是「臨床心理師考題 Agent」的持久狀態與正式版本來源。

## 最簡單的使用方式

在任何新對話，只要貼：

> `https://github.com/lily4318/clinical-psych-exam-agent 你的任務`

例如：

> `https://github.com/lily4318/clinical-psych-exam-agent 幫我做兒童版考卷`

> `https://github.com/lily4318/clinical-psych-exam-agent 幫我做兒童版10題考卷`

> `https://github.com/lily4318/clinical-psych-exam-agent 幫我輸出目前正式版Word`

AI 應自行先讀 `START_HERE.md` 與 `config/simulation_policy.yaml`，再載入 `release/current_release.yaml`、`agent/system_prompt.md` 與任務需要的 manifest／blueprint／題組／來源檔，不得要求使用者重新貼完整啟動說明或舊對話背景。

## 已經在同一個 Agent 對話中

若本對話已經載入本 Agent，之後可只下短指令，例如：

- `幫我做兒童版考卷`
- `幫我做成人版10題`
- `再出30題`
- `檢查甲乙卷是否等值`
- `輸出Word`

Agent 應自動沿用目前狀態。

## 分享給其他老師／研究者

直接把公開 repo 網址給對方即可。最推薦的分享文字只有一行：

> `https://github.com/lily4318/clinical-psych-exam-agent 請依這個Agent幫我做＿＿＿＿`

公開使用時，本 repo 預設為唯讀範本。如果對方只是使用 Agent，不需要 fork；如果希望長期保存自己的題目、審閱紀錄與正式版本，建議先 Fork 到自己的 GitHub，再改貼自己的 fork 網址。

## 新模擬測驗預設

- 歷屆考題範圍：使用**最新可取得的 5 個正式考試年度**，目前為民國 111–115 年；未來加入 116 年後自動變成 112–116 年。
- 未指定題數：直接做 **20 題**，不要先詢問題數。
- 指定 N 題：依指定題數生成。
- 若要求甲乙平行卷並指定 N 題：甲卷 N 題、乙卷 N 題。
- 非 20 題時需依領域藍圖比例衍生考點、難度與認知層次，不能只截短既有 20 題。

## 「X版」的解讀

- `兒童版`、`成人版` 等預設代表**命題內容領域／臨床族群領域**，不是作答者年齡。
- `兒童版考卷`＝兒童／青少年臨床心理領域；考生仍是臨床心理師國考程度。
- 只有明確說「給兒童作答」、「國小生作答」、「改成兒童看得懂」等，才調整真正作答者的閱讀程度。
- 新領域必須依近 5 年歷屆考題與可靠來源先建立該領域專屬藍圖。

## 核可與 Word

只有明確說出「核可／正式核可／批准」並指向版本、卷別或題組才算正式核可。

正式核可後：

- 若之前已要求 Word，直接產出。
- 若尚未要求 Word，Agent 主動詢問是否輸出 Word。

預設 Word 套件：甲卷、乙卷、答案與解析。

## 儲存來源

GitHub 是唯一持久 source of truth。原 Google Drive 已刪除，不再使用。
