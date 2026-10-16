# Clinical Psychologist Exam Agent

用於建立臺灣臨床心理師國考風格之模擬試題，現階段聚焦於「物質濫用與依賴之心理衡鑑與心理治療」。

## 目前版本

- 歷屆範圍：民國 110–115 年
- 已索引成癮／物質使用相關考點：74 個
- 已建立官方答案狀態：71 題選擇題＋3 題申論題
- 目標輸出：甲卷、乙卷各 20 題四選一單選題
- 平行卷：20 組配對題槽位（P01–P20）
- 已完成第一個完整人工審閱 release：`review-v0.1`（P01–P20，共 40 題；尚未由使用者最終核可）
- 生成策略：每次以一組 Pxx 同時生成甲乙兩題，直接控制等值性
- 最終核可：使用者

## 每卷 20 題藍圖

| 類別 | 題數 |
|---|---:|
| A DSM-5/DSM-5-TR 診斷、分類與行為成癮 | 4 |
| B 心理衡鑑、危險／保護因子、病因與共病 | 3 |
| C 動機式晤談 MI／改變動機 | 2 |
| D CBT／復發預防／行為治療 | 4 |
| E 生理心理機制、藥理、耐受／戒斷與獎賞系統 | 4 |
| F 三級預防、社區／家庭、政策與整合處遇 | 3 |

難度目標：基礎 2／中等 11／進階 7。  
認知層次目標：記憶 2／理解 8／應用 7／整合 3。

## Repository 角色

GitHub 是 Agent 的正式版本庫，保存提示詞、命題藍圖、歷屆考點索引、官方答案索引、權威知識來源、品質規則、資料結構與執行程式。Google Drive 保留官方 PDF、教材、文獻與原始工作檔。

若 GitHub 與 Google Drive 的命題規格不一致，以 GitHub 的 `config/` 正式版本為準，再視需要回寫 Drive 工作文件。

## 目錄

- `agent/`：Agent 角色與工作規則
- `config/`：命題藍圖、平行卷規格、pair-specific 核心來源、難度與來源優先序
- `data/historical_exam_index.csv`：110–115 年 74 個歷屆考點摘要索引
- `data/official_answer_keys.csv`：74 個索引題目的官方答案狀態
- `data/answer_source_catalog.csv`：考選部標準答案／更正答案來源
- `data/knowledge_sources.csv`：DSM、MI、CBT/RP、衡鑑、神經機制、藥理與臺灣政策權威來源索引
- `review/`：具版本價值的人工審閱題、reviewer 報告、release manifest 與 release notes
- `src/`：載入、來源選擇、Prompt、Provider、驗證、等值檢查、review 組卷與匯出流程
- `schemas/`：題目與考卷 JSON Schema
- `tests/`：pytest 自動測試與品質檢核案例
- `docs/`：Google Drive 原始資料位置與工作流程
- `output/`：本機產出的草稿考卷與解析；產物預設不提交 Git

## 快速開始

建議 Python 3.11 以上。

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -e ".[test]"
pytest
```

## 完整人工審閱版（review-v0.1）

`review/release_manifest_v0.1.yaml` 是目前 P01–P20 的唯一 canonical 組卷入口。它固定指向五個最新版批次：

- P01–P04 v0.2
- P05–P08 v0.2
- P09–P12 v0.2
- P13–P16 v0.2
- P17–P20 v0.2

組成完整甲乙卷：

```bash
clinical-psych-review-build
```

或：

```bash
python -m src.assemble_review_exam
```

組卷器在輸出完整卷前會重新檢查：P01–P20 是否完整、每卷 20 題、A–F 分布 4/3/2/4/4/3、難度 2/11/7、認知層次 2/8/7/3、指定答案位置、甲乙卷平行結構、歷屆來源、pair-specific 核心權威來源。任一硬性檢核失敗就不輸出完整審閱卷。

此版本一律維持 `approved_by_user=false` 與 `待複核`，直到使用者明確核可。

### 1. 產生結構測試版甲乙卷

```bash
python -m src.generate_exam --out output
```

會建立 `form_a.stub.json` 與 `form_b.stub.json`。這些題目只有結構用途，題幹與解析均標示 `[STUB]`，不可作為正式考題。

### 2. 匯出 20 組 source-grounded 產題請求

```bash
python -m src.export_prompt_pack --out output/pair_generation_requests.json
```

每個 P01–P20 request 都包含：

- 甲乙卷共同考點
- 難度與認知層次
- 甲乙卷各自指定的正確答案位置
- 最相關的歷屆考點摘要
- 對應的權威知識來源
- pair-specific 必須引用的核心來源
- 禁止近似改寫歷屆題、禁止無來源補造內容等限制

### 3. 驗證甲乙卷

```bash
python -m src.check_parallel_forms output/form_a.stub.json output/form_b.stub.json
```

檢查項目包括：

- 每卷是否恰為 20 題
- A–F 類別配置是否為 4/3/2/4/4/3
- 難度是否為 2/11/7
- 認知層次是否為 2/8/7/3
- P01–P20 是否一一對應
- 平行題的類別、難度與認知層次是否一致
- 甲乙卷題幹是否意外完全相同
- 來源 ID 是否存在於正式索引
- 答案位置是否過度失衡或有長串規律

### 4. 匯出 Markdown

```bash
python -m src.export_exam output/form_a.stub.json --out output
```

會輸出考卷 Markdown、答案解析 Markdown 與 JSON。

## 使用 OpenAI Responses API 產生草稿

這是可選功能。API key 與模型名稱都不會寫入 repository。

安裝：

```bash
pip install -e ".[test,openai]"
```

設定環境變數：

```bash
# macOS / Linux
export OPENAI_API_KEY="..."
export OPENAI_MODEL="<你要使用且帳號可存取的模型>"

# Windows PowerShell
$env:OPENAI_API_KEY="..."
$env:OPENAI_MODEL="<你要使用且帳號可存取的模型>"
```

執行：

```bash
python -m src.run_openai_generation --out output/openai-draft
```

或安裝後直接執行：

```bash
clinical-psych-exam-openai --out output/openai-draft
```

流程會依序：

1. 讀取正式藍圖與 P01–P20。
2. 為每組題目選出最相關的歷屆考點摘要與權威來源。
3. 一次要求模型生成同一 Pxx 的甲乙兩題。
4. 強制核對題號、類別、難度、認知層次、指定答案位置與 pair-specific 核心來源。
5. 執行整份甲乙卷等值檢核。
6. 若有 error，停止正式匯出並保留 `parallel_form_check.json`。
7. 只有通過結構檢核後，才輸出 JSON、考卷 Markdown 與答案解析 Markdown。

即使程式檢核通過，產出的內容仍只屬「草稿」，不會自動變成「已核可」。

## 正式題目供應器架構

`src/provider.py` 提供兩種主要接法：

- `CallbackQuestionProvider`：一次生成一題。
- `CallbackPairQuestionProvider`：一次生成同一 Pxx 的甲乙兩題；正式出題優先使用此方式。

`src/openai_provider.py` 則把 OpenAI Responses API 包成 JSON callback。repo 不綁死任何模型名稱，也不保存 API key。

## GitHub Actions 狀態

此 private repository 目前在 GitHub Actions 建立 job 前會回傳 `startup_failure`。為避免每次 push 都產生無意義的失敗紀錄，自動 push trigger 暫時停用，只保留手動 `workflow_dispatch`。待 repository／account 的 Actions 執行設定排除後，再恢復自動 CI。

這不代表 pytest 已在 GitHub runner 上通過；repo 內仍保留完整 pytest 測試，包含 canonical review release 的 P01–P20 組卷測試。

## 核心原則

1. 先建立藍圖，再出題。
2. 不直接改寫歷屆題原文，只抽取考點與命題風格。
3. 甲乙卷同考點、同認知層次、同目標難度，但採不同情境。
4. DSM、MI、CBT/RP、生理心理機制等關鍵內容必須有可靠來源。
5. 不確定的資訊標記為待查證，不可自行補造。
6. 每題應有單一最佳答案、逐項解析與來源依據。
7. 程式自動檢核只處理可形式化規則；內容正確性與題目品質仍需人工複核。
8. 最終發布前必須由使用者人工核可。
