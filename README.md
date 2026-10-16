# Clinical Psychologist Exam Agent

用於建立臺灣臨床心理師國考風格之模擬試題，現階段聚焦於「物質濫用與依賴之心理衡鑑與心理治療」。

## 目前版本

- 歷屆範圍：民國 110–115 年
- 已索引成癮／物質使用相關考點：74 個
- 目標輸出：甲卷、乙卷各 20 題四選一單選題
- 平行卷：20 組配對題槽位（P01–P20）
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

GitHub 是 Agent 的正式版本庫，保存提示詞、命題藍圖、歷屆考點索引、品質規則、資料結構與執行程式。Google Drive 保留官方 PDF、教材、文獻與原始工作檔。

## 目錄

- `agent/`：Agent 角色與工作規則
- `config/`：命題藍圖、平行卷規格、難度與來源優先序
- `data/`：110–115 歷屆考點索引與官方來源
- `src/`：可執行的載入、產題介面、驗證、等值檢查與匯出流程
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

### 1. 產生結構測試版甲乙卷

```bash
python -m src.generate_exam --out output
```

會建立 `form_a.stub.json` 與 `form_b.stub.json`。這些題目只有結構用途，題幹與解析均標示 `[STUB]`，不可作為正式考題。

### 2. 驗證甲乙卷

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
- 答案位置分布是否過度失衡或有長串規律

### 3. 匯出 Markdown

```bash
python -m src.export_exam output/form_a.stub.json --out output
```

會輸出考卷 Markdown、答案解析 Markdown 與 JSON。

## 正式題目供應器

`src/provider.py` 定義 `QuestionProvider` 介面。目前內建 `StubQuestionProvider`，目的是讓整個 Agent 在沒有任何 API key 的情況下仍可測試。

正式接入模型時，只需實作：

```python
generate_item(spec, form, item_id, source_ids) -> dict
```

回傳內容需符合 `schemas/item.schema.json`。API key 應透過環境變數或秘密管理服務提供，禁止寫入 repository。

## 核心原則

1. 先建立藍圖，再出題。
2. 不直接改寫歷屆題原文，只抽取考點與命題風格。
3. 甲乙卷同考點、同認知層次、同目標難度，但採不同情境。
4. DSM、MI、CBT/RP、生理心理機制等關鍵內容必須有可靠來源。
5. 不確定的資訊標記為待查證，不可自行補造。
6. 每題應有單一最佳答案、逐項解析與來源依據。
7. 自動檢核通過不等於內容已核可；最終版本仍需由使用者人工核可。
