---
name: exam-compose
description: 單一命題Agent根據真實領域藍圖及零額外付費推論生成兒少／成人臨床國考甲乙平行卷JSON；適用「命題、甲乙、N題、再出題」。
---
# 甲乙真實命題技能
遵守 `START_HERE.md`、`config/simulation_policy.yaml`、`agent/system_prompt.md`、`docs/AGENT_ARCHITECTURE_V2.md`；先取得 `exam-evidence-blueprint` 的可核查來源與該領域藍圖。
1. 查明**實際可用且零額外付費**的推論途徑（如當前環境真可執行的Ollama或已有平台推論）。免費Actions不等於免費LLM；沒有就分類 `model_unavailable`，不能改用付費API、Stub、FakeModel或無來源假題冒充完成。
2. 預設甲乙每卷20題，指定N則各N。建立P01–PN配對，同學習目標／目標難度／認知層次，情境實質不同；**不得宣稱未經考生實測的實證等值**。
3. 每題輸出題幹、A–D四選項、單一最佳答案、正解解析及A／B／C／D各自非空解析、考點、難度、認知層次、非空去重來源ID／實際支持位置，並標記未經獨立專家驗證。
4. 使用現有 `src/child_exam_pipeline.py`／schema驗證兩份真JSON；高風險內容再做實際來源查核，不能以單Agent自評當獨立專家驗收。
**完成**：真實推論證據＋甲乙各N題有效JSON及版本／來源可追溯。正式formal資料不可覆寫，缺推論就記阻礙。
