# START HERE｜臨床心理師考題 Agent

如果你是 ChatGPT／其他可讀取公開 GitHub 的 AI：**看到這個 repository 網址與使用者任務後，請直接執行，不要要求使用者貼一長串啟動指令。**

## 最短使用方式

使用者可以只輸入：

> `https://github.com/lily4318/clinical-psych-exam-agent 幫我做兒童版考卷`

或任何「repo 網址＋一句任務」，例如：

- `https://github.com/lily4318/clinical-psych-exam-agent 幫我做兒童版考卷`
- `https://github.com/lily4318/clinical-psych-exam-agent 幫我做成人版考卷`
- `https://github.com/lily4318/clinical-psych-exam-agent 幫我出20題新的物質濫用題`
- `https://github.com/lily4318/clinical-psych-exam-agent 幫我把正式版輸出成Word`

## AI 自動啟動流程

收到 repo 網址＋任務後，AI 應自行：

1. 讀取 `START_HERE.md`。
2. 讀取 `release/current_release.yaml`。
3. 讀取 `agent/system_prompt.md`。
4. 視任務需要讀取 current release 指向的 formal/review manifest、blueprint、題組與來源檔。
5. 直接執行使用者任務；不要要求使用者重貼 repo 背景、版本資訊或舊對話內容。

除非缺少一個會實質改變結果且無法合理預設的關鍵條件，否則不要先用一連串問題阻斷工作。可採合理預設時，應先執行並清楚標示預設。

## 短指令解讀規則

### 「X版考卷」預設代表命題領域，不是考生年齡

當使用者只說「幫我做 X 版考卷」時，**X 預設解讀為考題內容領域／臨床族群領域**，不是把題目寫成給該族群本人作答。

例如：

- `兒童版考卷`＝以兒童／青少年臨床心理之心理衡鑑、心理病理、心理治療與相關核心概念為命題領域；**考生仍是臨床心理師國考程度**。
- `成人版考卷`＝成人臨床心理相關領域；考生仍是臨床心理師國考程度。
- 若使用者說 `給兒童作答`、`國小生要作答`、`把文字改成兒童看得懂`，才代表要調整實際受試者／作答者的閱讀程度。

因此，不得因為看到「兒童版」就自動簡化成兒童閱讀程度、兒童測驗或兒童自己作答的題目。

### 其他預設

- 預設沿用目前 Agent 的核心命題流程、品質規則、來源要求、平行卷與版本管理原則。
- 若使用者沒有指定題數，沿用該任務既有設定；若是全新領域且沒有既有設定，可先依本 Agent 的 20 題甲乙卷框架建立候選藍圖。
- 若是新的命題領域，應先從歷屆考題／官方來源建立該領域的考點藍圖，再生成題目；不可把現有「物質濫用與依賴」的內容藍圖直接套到其他領域。
- 若使用者說「正式核可／核可／批准」並指向版本或卷別，才進入正式 release 流程。

## 公開分享模式

任何人都可以把本公開 repo 網址貼給自己的 AI 使用。

### 只想使用 Agent

直接貼「repo 網址＋任務」即可。此模式預設**唯讀使用本 repo**，不應修改原作者 repository。

### 想建立自己的長期版本

建議先 Fork 本 repository 到自己的 GitHub，再把自己的 fork 網址貼給 AI。這樣自己的題目、review、release 與 `current_release.yaml` 才能持續保存，不會和原作者版本混在一起。

## 持久狀態

本 Agent 的持久 source of truth 是 GitHub。Google Drive 已刪除，不得要求尋找舊 Drive 資料。

目前狀態入口：`release/current_release.yaml`。
