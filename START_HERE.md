# START HERE｜臨床心理師考題 Agent

如果你是 ChatGPT／其他可讀取公開 GitHub 的 AI：**看到這個 repository 網址與使用者任務後，請直接執行，不要要求使用者貼一長串啟動指令。**

## 最短使用方式

使用者可以只輸入：

> `https://github.com/lily4318/clinical-psych-exam-agent 幫我做兒童版考卷`

或任何「repo 網址＋一句任務」，例如：

- `https://github.com/lily4318/clinical-psych-exam-agent 幫我做兒童版考卷`
- `https://github.com/lily4318/clinical-psych-exam-agent 幫我做成人版考卷`
- `https://github.com/lily4318/clinical-psych-exam-agent 幫我做兒童版10題考卷`
- `https://github.com/lily4318/clinical-psych-exam-agent 幫我把正式版輸出成Word`

## AI 自動啟動流程

收到 repo 網址＋任務後，AI 應自行：

1. 讀取 `START_HERE.md`。
2. 讀取 `config/simulation_policy.yaml`。
3. 讀取 `release/current_release.yaml`。
4. 讀取 `agent/system_prompt.md`。
5. 視任務需要讀取 current release 指向的 formal/review manifest、該領域 blueprint、題組與來源檔。
6. 直接執行使用者任務；不要要求使用者重貼 repo 背景、版本資訊或舊對話內容。

除非缺少一個會實質改變結果且無法合理預設的關鍵條件，否則不要先用一連串問題阻斷工作。

## 模擬測驗的固定預設

### 歷屆考題範圍：最近 5 個可取得年度

新的模擬測驗一律以**資料庫中最新可取得的 5 個正式考試年度**作為歷屆考題分析範圍，不把年份永久寫死。

目前資料最新到民國 115 年，因此目前視窗是 **111–115 年**。未來加入 116 年正式考題後，應自動改為 **112–116 年**。

詳細規則見 `config/simulation_policy.yaml`。

### 題數：未指定就直接做 20 題

- 使用者**沒有指定題數**：直接使用預設 **20 題**，不要先詢問題數。
- 使用者**有指定題數**：照指定題數生成，例如「做 10 題」就是 10 題。
- 若要求甲乙平行卷並指定 N 題：**甲卷 N 題、乙卷 N 題**。
- 只有題數不是有效正整數或指令互相矛盾時，才需要追問。
- 指定題數不是 20 時，必須依該領域藍圖按比例重新配置考點、難度與認知層次，不能只把 20 題截短。

## 短指令解讀規則

### 「X版考卷」預設代表命題領域，不是考生年齡

當使用者只說「幫我做 X 版考卷」時，**X 預設解讀為考題內容領域／臨床族群領域**，不是把題目寫成給該族群本人作答。

例如：

- `兒童版考卷`＝兒童／青少年臨床心理領域；**考生仍是臨床心理師國考程度**。
- `成人版考卷`＝成人臨床心理領域；考生仍是臨床心理師國考程度。
- 只有使用者明確說 `給兒童作答`、`國小生要作答`、`改成兒童看得懂`，才調整真正作答者的閱讀程度。

若是新的命題領域，應先從最近 5 個可取得年度的歷屆考題與可靠來源建立該領域專屬考點藍圖，再生成題目；不得把「物質濫用與依賴」的內容藍圖直接套用到其他領域。

## 公開分享模式

任何人都可以把本公開 repo 網址貼給自己的 AI 使用。

### 只想使用 Agent

直接貼「repo 網址＋任務」即可。此模式預設**唯讀使用本 repo**，不應修改原作者 repository。

### 想建立自己的長期版本

建議先 Fork 本 repository 到自己的 GitHub，再把自己的 fork 網址貼給 AI。這樣自己的題目、review、release 與 `current_release.yaml` 才能持續保存，不會和原作者版本混在一起。

## 持久狀態

本 Agent 的持久 source of truth 是 GitHub。Google Drive 已刪除，不得要求尋找舊 Drive 資料。

目前狀態入口：`release/current_release.yaml`。
