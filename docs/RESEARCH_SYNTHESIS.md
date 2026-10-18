# 研究綜述：對考題 Agent 的十二個直接決策依據
日期：2026-10-18。這份是已檢視資料頁/摘要後的**重點綜合**，不是宣稱逐篇通讀100份全文或重現其實驗。完整100筆資料：[研究資源索引](ML_AGENT_RESEARCH_100_SOURCES.md)。

| 來源 | 查得重點 | 本Agent落地決策 |
|---|---|---|
| [Google ML Crash Course — 資料切分](https://developers.google.com/machine-learning/crash-course/overfitting/dividing-datasets) | 訓練、validation與test用途不同；測試集反覆使用會失去獨立性 | 每小時只用開發集，真正封存測試僅在候選版凍結後啟封 |
| [Google Cloud MLOps架構](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning) | 真正ML生產系統的關鍵還包含版本、資料、測試、監控與流程編排 | 不把「prompt更新」等同底層模型權重訓練；建構可稽核 pipeline |
| [Anthropic 2026 Agent Evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | Agent要追蹤真實outcome、trace、grader種類、反覆trial與回歸能力 | 建立終局任務成功率/步驟工具品質的不同軌道 |
| [Anthropic 多Agent研究實務](https://www.anthropic.com/engineering/multi-agent-research-system) | 多Agent對可平行大型研究有用，但token成本顯著增加 | 避免一開始就為每小時小改動使用大型多Agent訓練 |
| [Microsoft Foundry agent evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators) | 端對端任務與工具流程需要不同評測項目 | 模擬「簡短指令→讀GitHub→生成→Word→版本管理」全流程 |
| [AWS AgentCore評測](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html) | 可用多層trace和自訂scorer，結合自動評測與人工審查 | 靜態規則交給code；醫學內容交給可核實來源與領域專家 |
| [LangChain 2026評測檢查表](https://www.langchain.com/blog/agent-evaluation-readiness-checklist) | 先少量真實trace、明確成功條件，再擴充 | 先20-50真實任務建baseline，再放大資料集 |
| [OpenAI模型優化](https://developers.openai.com/api/docs/guides/model-optimization) | eval→prompt→測試的反饋迴圈先於重訓；產品介面可能變更 | 不依賴即將淘汰的legacy Evals介面，採可攜資料與記錄 |
| [2026 ACL Agent 評測回顧](https://aclanthology.org/2026.findings-acl.1330/) | 評估挑戰含安全性、成本、強韌性與細粒度評測 | 加入成本、來源與失敗類型等附屬指標 |
| [2025 ICML benchmark污染研究](https://proceedings.mlr.press/v267/sun25t.html) | 題目改寫未必能有效解除污染、也可能犧牲內容一致性 | 不把歷屆題改寫視為新盲測；封存題要來源分隔 |
| [2026 AI 醫學MCQ有效性系統回顧](https://pubmed.ncbi.nlm.nih.gov/42160214/) | 效度證據多偏專家內容審查，較少包含反應歷程、內在結構與後果；不支持未經人工監督的高風險正式測驗 | 專家90%只是階段門檻，增加實測難度/鑑別度/信度等 |
| [NBME題目編寫指南](https://www.nbme.org/institutions/nbme-item-writing-guide/) | 單一最佳答案、臨床情境品質、選項與心理計量都是題目品質核心 | 使用明確rubric、逐項解析、誘答選項與校準資料 |

## 研究品質區分
- **學術研究**：區分已審查論文、預印本、系統回顧與實證研究；不因研究數量多就視為結論確定。
- **企業實務**：可作工程方法參考，但雲端產品限制、費用與可用性須依當期官方文件重新查證。
- **出題心理計量**：專家核可/雙模型互驗不足以證明正式考試可用；需真實考生與有效度論證。

## 尚未完成
1. 100份來源目前已建立可查索引，但**尚未逐篇全文閱讀／影音觀看與完整批判性評讀**。後續應標記每筆摘要檢視、全文評讀與可重現程度，避免虛報。
2. 尚未在可執行runner完成pytest與真正模型生成benchmarks。
3. 尚未取得至少100題全新、私有且獨立專家標註的正式盲測資料；90%仍屬未驗證目標。
4. 尚未取得考生作答樣本，不能推估模擬卷的實際鑑別度與信度。
