# Clinical Psychologist Exam Agent

用於建立臺灣臨床心理師國考風格之模擬試題，目前聚焦於「物質濫用與依賴之心理衡鑑與心理治療」。

## 目前正式狀態

- 歷屆範圍：民國 110–115 年
- 已索引成癮／物質使用相關考點：74 個
- 正式核可版本：`formal-v1.0`
- 來源審閱版本：`review-v0.2`
- 正式核可日期：2026-10-16
- 核可範圍：甲卷 P01–P20、乙卷 P01–P20，共 40 題
- 最終核可權：使用者

目前狀態入口：`release/current_release.yaml`。

## 唯一持久來源

**GitHub repository `lily4318/clinical-psych-exam-agent` 是目前唯一的持久狀態、正式版本與 Agent 規則來源。**

原 Google Drive 已由使用者刪除，不再屬於本 Agent 架構的一部分。Agent 不得假定舊 Google Drive、Google Docs、Google Sheets 或其中原始檔仍存在。若未來需要新的 PDF、教材、文獻或其他原始檔，必須重新上傳、提供新來源，或另行指定新的持久儲存位置。

## 新對話接續

換新 ChatGPT 對話時，不需要重新敘述整個專案。先讓 Agent 讀：

1. `release/current_release.yaml`
2. `agent/system_prompt.md`
3. `docs/NEW_CHAT_CONTINUATION.md`
4. `current_release` 指向的 formal／review manifest

建議在新對話貼上：

> 請接續我的「臨床心理師考題 Agent」。GitHub repo 是 lily4318/clinical-psych-exam-agent。請先讀 release/current_release.yaml、agent/system_prompt.md、docs/NEW_CHAT_CONTINUATION.md，以及 current_release 指向的 formal/review manifest，再告訴我目前正式版本、進行狀態與可繼續的下一步。GitHub 是目前唯一持久來源；不要依賴舊對話記憶，也不要尋找已刪除的 Google Drive。

## 每卷藍圖

| 類別 | 題數 |
|---|---:|
| A DSM-5/DSM-5-TR 診斷、分類與行為成癮 | 4 |
| B 心理衡鑑、危險／保護因子、病因與共病 | 3 |
| C 動機式晤談 MI／改變動機 | 2 |
| D CBT／復發預防／行為治療 | 4 |
| E 生理心理機制、藥理、耐受／戒斷與獎賞系統 | 4 |
| F 三級預防、社區／家庭、政策與整合處遇 | 3 |

難度：基礎 2／中等 11／進階 7。  
認知層次：記憶 2／理解 8／應用 7／整合 3。

## 版本治理

`release/formal_release_v1.0.yaml` 以 Git blob SHA 鎖定正式核可當下的五個題組。既有 formal release 不得覆寫。

未來若修改題目、增加新主題或建立新卷，流程固定為：

1. 建立新的 review 版本；
2. 完成人工審閱與品質檢核；
3. 使用者明確表示「核可／正式核可／批准」；
4. 建立新的 formal 版本。

「可以」、「差不多可以」、「看起來不錯」、「繼續」不構成正式核可。

## Word 輸出規則

正式核可後：

- 若使用者已經要求 Word，Agent 直接輸出，不再重問。
- 若尚未要求 Word，Agent 必須主動詢問一次是否輸出 Word。
- 預設輸出三個 `.docx`：甲卷、乙卷、答案與解析。
- Word 必須依 manifest 鎖定內容產生，檔名包含正式版本號，且交付前需做版面 QA。

詳細規則：`agent/word_export_policy.md`。

## Repository 目錄

- `agent/`：Agent 角色、system prompt、reviewer 與 Word 輸出規則
- `config/`：命題藍圖、平行卷規格、來源要求
- `data/`：歷屆考點、官方答案與知識來源索引
- `review/`：人工審閱題組、manifest、reviewer 紀錄與測試報告
- `release/`：正式核可版本與 current release 狀態
- `src/`：載入、來源選擇、Prompt、驗證、組卷與匯出流程
- `schemas/`：題目與考卷 JSON Schema
- `tests/`：pytest 品質檢核案例
- `docs/`：跨對話接續等操作文件
- `output/`：本機產出；預設不提交 Git

## 常用命令

```bash
python -m src.assemble_review_exam
python -m src.check_parallel_forms output/form_a.stub.json output/form_b.stub.json
python -m src.export_exam output/form_a.stub.json --out output
```

安裝後亦可使用：

```bash
clinical-psych-review-build
clinical-psych-exam-check
clinical-psych-exam-export
clinical-psych-user-review
```

## GitHub Actions 狀態

此 private repository 先前在 GitHub Actions 建立 job 前出現 `startup_failure`，因此自動 push trigger 暫停，只保留手動 `workflow_dispatch`。這不代表 pytest 已在 GitHub runner 上通過；在實際成功執行前不得宣稱 CI／tests 已通過。

## 核心原則

1. 先建立藍圖，再出題。
2. 不直接重製歷屆題原文，只抽取考點與命題風格。
3. 甲乙卷同考點、同認知層次、同目標難度，但採不同情境。
4. DSM、MI、CBT/RP、生理心理機制等關鍵內容必須有可靠來源。
5. 不確定資訊標記為待查證，不自行補造。
6. 每題需有單一最佳答案、逐項解析與來源依據。
7. 自動檢核不等於人工核可；正式發布必須由使用者明確核可。
