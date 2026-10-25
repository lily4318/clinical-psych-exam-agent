# Clinical Psychologist Exam Agent

用於建立臺灣臨床心理師國考風格之模擬試題與甲乙平行卷。

## 最短使用方式

把 repository 網址貼給可讀取公開 GitHub 的 AI，再加一句任務即可：

> `https://github.com/lily4318/clinical-psych-exam-agent 幫我做兒童版考卷`

AI 應先讀 `START_HERE.md`，再依 repository 規則自動載入狀態與命題流程，不要求使用者重貼背景。

## 新模擬測驗的預設規則

### 歷屆考題：最近 5 個可取得正式考試年度

不再固定寫死 110–115 年。新模擬測驗會從 `data/historical_exam_index.csv` 中取得最新的 5 個不同考試年度。

目前資料最新到民國 115 年，因此目前使用 **111–115 年**。未來加入 116 年正式考題後，應自動改為 **112–116 年**。

### 題數：預設 20 題，但可指定

- 未指定題數：直接生成 **20 題**，不要先詢問題數。
- 指定 N 題：依指定題數生成。
- 若要求甲乙平行卷並指定 N 題：甲卷 N 題、乙卷 N 題。
- 非 20 題時，應按該領域基準藍圖比例重新配置考點、難度與認知層次，不得只截短既有 20 題藍圖。

詳細政策：`config/simulation_policy.yaml`。

## 「兒童版」等短指令的意義

`兒童版考卷` 預設代表**兒童／青少年臨床心理命題領域**，不是讓兒童本人作答；考生仍是臨床心理師國考程度。

只有使用者明確說「給兒童作答」、「國小生要作答」、「改成兒童看得懂」等，才調整真正作答者的閱讀程度。

新命題領域必須先依最近 5 個可取得年度的歷屆考題與可靠來源建立專屬考點藍圖，不得直接套用現有物質濫用領域的內容藍圖。

## 目前正式狀態

- 正式核可版本：`formal-v1.0`
- 來源審閱版本：`review-v0.2`
- 正式核可日期：2026-10-16
- 核可範圍：甲卷 P01–P20、乙卷 P01–P20，共 40 題
- 目前狀態入口：`release/current_release.yaml`

`formal-v1.0` 是既有正式快照，不因新的近 5 年／可變題數政策而回頭改寫。

## 唯一持久來源

**GitHub repository `lily4318/clinical-psych-exam-agent` 是目前唯一的持久狀態、正式版本與 Agent 規則來源。**

原 Google Drive 已刪除，不再屬於本 Agent 架構。若未來需要新的 PDF、教材、文獻或原始檔，需重新提供並記錄新的來源。

## 公開分享

其他研究者或老師可以直接使用公開 repo 網址＋一句任務。

若只是使用 Agent，應把原作者 repo 視為唯讀範本；若要長期保存自己的題目、review、release 與 current state，建議先 Fork 本 repository，再使用自己的 fork。

## 重要檔案

- `START_HERE.md`：公開分享與一句話啟動入口
- `config/simulation_policy.yaml`：近 5 年與題數預設政策
- `release/current_release.yaml`：目前 Agent 狀態入口
- `agent/system_prompt.md`：核心命題與版本規則
- `agent/word_export_policy.md`：正式核可後 Word 輸出規則
- `config/blueprint.yaml`：既有 20 題物質濫用正式版本基準藍圖
- `data/historical_exam_index.csv`：歷屆考點索引
- `data/knowledge_sources.csv`：權威知識來源索引
- `review/`：人工審閱版本與 reviewer 紀錄
- `release/`：使用者正式核可版本紀錄
- `src/`：載入、來源選擇、Prompt、驗證、組卷與匯出程式
- `tests/`：品質與版本測試

## 來源與品質原則

1. 先建立考點藍圖，再出題。
2. 不直接重製歷屆題原文，只抽取考點、認知要求與命題風格。
3. DSM、MI、CBT/RP、生理心理、藥理等關鍵內容必須有可靠來源。
4. 每題需有單一最佳答案與合理干擾選項。
5. 平行卷需維持考點、難度、認知層次與推理負荷等值，但使用不同情境。
6. 未經使用者明確「核可／正式核可／批准」，不得升為正式版本。
7. 既有 formal release 不得覆寫；修改正式題目必須建立新的 review → 核可 → formal 版本。

## Word 輸出

### 新模擬考卷：直接交付兩份 Word，不等待使用者核可

建立甲乙平行卷時，完成命題與自動檢核後應直接交付 **甲卷、乙卷各一份 DOCX**；各卷預設將答案及解析附在後面。自動交付不等於正式核可，不得更新 `formal-v1.0` 或標記為專家驗收合格。

當兩卷結構化 JSON 已存在時，可透過免費、無模型 API 的匯出工具執行：

```bash
clinical-psych-exam-docx output/form_a.json output/form_b.json --out output/docx
```

如需提供不含解答的考生版，加上 `--hide-answers`。

若要從**現有已驗證的物質濫用領域 review-v0.2** 直接產出甲乙各20題 Word，則可一行執行：

```bash
clinical-psych-review-docx --out output/review-docx
```

此指令從既有 review manifest 組卷並輸出兩份可閱讀 DOCX；它不會自行產生兒童領域新題，也不會把 review 草稿升為正式核可版。匯出器只負責既有 JSON → DOCX；兒童或其他新領域的 AI 命題尚須完成對應藍圖及生成服務整合。若執行環境不能實際建立檔案，不得宣稱已產生下載檔。

### 兒童／青少年新題：本機零額外付費模型的快速檢查

本機 CLI 可選用**使用者已安裝**的 Ollama 模型；GitHub Actions 的 pytest 不會替你下載模型，也無法連線到使用者電腦的 localhost。先檢查本機模型是否已安裝、服務是否啟動（只讀取本機模型清單，**不命題、不下載、不呼叫付費 API**）：

```bash
python -m src.child_exam_pipeline --check-local-model --model qwen2.5
```

模型名稱請換成自己已安裝的模型。若檢查失敗，程式會在讀取或抓取來源、執行20次配對命題之前停止；不會默默切換雲端模型。確認成功後才執行：

```bash
python -m src.child_exam_pipeline --auto-evidence --model qwen2.5 --items 20 --out output/child-docx
```

這條命令仍須本機有可用 Ollama、網路可存取官方臨床指引、且模型確實產出符合規範的題目；來源或命題不足時應拒絕交付。**本機預檢成功不代表完成真實 AI 命題、專家臨床驗證或 ChatGPT 首次雙 Word 下載。** ChatGPT 等其他平台可以直接使用自己的已授權工具製作 DOCX，**不需要安裝 Ollama**。

### 既有正式版

正式核可後按 `agent/word_export_policy.md`，維持甲卷、乙卷、答案與解析三個 DOCX 的正式版本交付規範；未經核可不得改變正式版本。

## 開發／測試註記

既有 20 題 P01–P20 executable pipeline 仍保留，用於目前 formal-v1.0 基準與相關測試。新的 Agent 對話層已支援「未指定 20 題、指定則依指定題數」的政策；非 20 題應建立衍生藍圖，不得覆寫既有正式基準。

GitHub Actions 先前曾在 job 建立前出現 `startup_failure`；因此不要把 repository 中存在 pytest 測試解讀成 CI 已成功通過。除非實際執行測試並得到結果，否則不得宣稱 tests pass。

## 每小時自動優化與評測

目前排程每小時執行一次低風險 Agent 流程優化。評測政策：[`config/ml_evaluation_policy.yaml`](config/ml_evaluation_policy.yaml)；實作及資料隔離說明：[`docs/EVALUATION_GUIDE.md`](docs/EVALUATION_GUIDE.md)。現有公開資料的111–114年48筆為訓練／開發診斷、115年14筆為非盲測診斷。真正的**90%**須由全新、獨立標註之模擬題驗收；目前尚未證明達標，也沒有重新訓練底層模型權重。

## 企業式 Agent 長期優化（2026-10）

- [百項機器學習／Agent 評測研究資源](docs/ML_AGENT_RESEARCH_100_SOURCES.md)：整理100項不重複文獻、各企業技術文件與評測工具；屬研究索引，不代表已完整閱讀所有全文。
- [長期評測目標與五軌 KPI](docs/LONG_TERM_EVALUATION_ROADMAP.md)：涵蓋回歸測試、Agent任務成功率、獨立專家試題品質90%、心理計量驗證與運維成本。
- [GitHub連線、Actions故障檢查](docs/GITHUB_CONNECTION_TROUBLESHOOTING.md)：附可手動執行的 `.github/workflows/connectivity_smoke.yml`。
- 每小時自動化以開發集/非封存測試資料做受限迭代；沒有真正獨立盲測與人類專家審查，不得宣稱品質已達90%。
