# 後續逐篇研讀追蹤
日期：2026-10-18

- 100 筆可追溯網路研究/技術來源：`docs/ML_AGENT_RESEARCH_100_SOURCES.md`（100/100已建索引；非100份全文讀完）。
- 代表性研究內容歸納：`docs/RESEARCH_SYNTHESIS.md`（12項重點來源）。
- 詳盡全文/完整影音批判性評讀：**尚未完成100/100**；此欄不可用「索引完成」取代。
- 每輪從尚未詳閱的來源選擇最多3項，記錄日期、原文類型、取得深度（摘要/全文/影片）、對Agent的具體行動、可能的利益衝突、引用與驗證需求。避免反覆對同一網址加計篇數。
- 若來源有存取限制，標為受限，不能虛報全文閱讀；如有可採取的工程方案先經開發集測試，不觸碰正式題目與封存測試集。

## 已有專題歸納（非完整全文驗證）
Google MLCC資料切分、Google Cloud MLOps、Anthropic Agent Evals、Anthropic多Agent研究、Microsoft Foundry、AWS AgentCore、LangChain eval readiness、OpenAI model optimization、ACL2026 survey、ICML2025污染評估、2026醫學MCQ有效性系統回顧、NBME item-writing指南。摘要參見 `docs/RESEARCH_SYNTHESIS.md`。


## 2026-10-18 16:00 研究與測試紀錄

本輪檢視以下3份尚未登錄逐項閱讀紀錄的 Google 官方網頁正文，未複現範例或執行影片：
- [008 Deployment testing](https://developers.google.com/machine-learning/crash-course/production-ml-systems/deployment-testing)：頁面更新2025-08-25；整合測試、版本對比與部署前品質門檻。應用：補齊程式品質門檻測試。
- [004 Data characteristics](https://developers.google.com/machine-learning/crash-course/overfitting/data-characteristics)：頁面更新2025-12-03；標註錯誤、重複與缺漏資料影響品質。應用：缺少專家標註不得自動補成合格。
- [009 Questions to ask](https://developers.google.com/machine-learning/crash-course/production-ml-systems/questions)：頁面更新2025-12-03；資料來源可靠性及回饋迴圈。應用：禁止封存測試結果流入每小時調整。

證據限制：三者是一般機器學習工程教材，並非臨床心理試題品質的直接效度研究。本輪未進行模型微調或臨床專家評分。

本輪新增6項品質門檻回歸測試，commit `7348f6ba9d575546876e80f6fc1f8961d047e9c8`。使用GitHub取得的評測程式與測試內容在本地重建最小環境執行10/10通過；不是完整repo pytest或CI。歷屆索引74筆：111–114年48筆開發、115年14筆歷史診斷，非盲測。正式90%尚未驗證。GitHub Actions最近仍是2026-10-16的startup_failure。


## 2026-10-18 16:56 研究研讀與資料洩漏稽核

本輪新增檢視三項100篇索引中尚未逐項登錄的來源；均為公開官方網頁正文，未下載附屬資料、執行SDK或重現實驗：
- **#010 Google Cloud — MLOps CI/CD/CT**：https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning；官方文件最近審閱2024-08-28；已檢視資料驗證、模型驗證、pipeline metadata、觸發條件等主要章節。應用：將資料版本/來源家族、實驗版本與執行結果記錄為不可混淆的獨立指標。限制：主要針對預測式ML，非直接的臨床考題效度證據。
- **#014 Microsoft Foundry — Evaluate your AI agents**：https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluate-agent；官方文件更新2026-10-01；已檢視rubric evaluator、任務資料集、工具與安全評測及版本比較的主要章節。應用：明確分開工具呼叫、任務完成、品質與安全的評分。限制：SDK示例依賴Foundry與Azure模型部署，未在本專案安裝或付費測試。
- **#032 LangChain — The Most Common Questions About Agent Evals, Answered**：https://www.langchain.com/blog/common-questions-about-agent-evals；發布2026-10-15；已檢視正文（baseline、offline/online eval、程式評分、LLM judge與人工校準、完整任務狀態、成本控制）。應用：先用10–20真實任務trace建立單項行為baseline，與封存專家盲測分開。限制：企業產品實務文章，未複現範例；不可直接推論臨床試題準確率。

**本輪資料治理新發現**：`data/historical_exam_index.csv`只有`item_id/year/source_item`等欄位，沒有可用來辨識跨年度同源改寫的`origin_group_id`。現有`chronological_diagnostic_split`只檢查item_id是否重複，不能證明同源題組沒有跨開發與歷史診斷分區。已在隔離環境對候選同源群組檢核函式執行4/4單元測試（非完整repo pytest）；程式提交因連接器安全檢查阻擋，未將此候選修正寫回repo。下一步應先為新收集的資料建立來源家族ID並進行群組洩漏檢查，不能把「按年份切分」誤稱已排除同源污染。

GitHub Actions本輪查得仍為67筆執行紀錄，最新2026-10-16 `startup_failure`，未見smoke workflow成功紀錄。正式專家盲測0題可用，90%仍未驗證；未進行模型訓練、未更改formal-v1.0。
