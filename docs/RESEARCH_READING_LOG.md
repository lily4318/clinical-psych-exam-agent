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
