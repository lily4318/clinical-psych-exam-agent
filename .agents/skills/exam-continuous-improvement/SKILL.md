---
name: exam-continuous-improvement
description: 每小時或手動「繼續、卡住、訓練、優化」時重查GitHub、實際修正單一可回退問題，保留跨對話狀態、證據及五軌KPI。
---
# 跨對話接續、故障恢復與優化
每輪先讀使用者要求的九份：`START_HERE.md`、`release/current_release.yaml`、`config/simulation_policy.yaml`、`config/ml_evaluation_policy.yaml`、`docs/LONG_TERM_EVALUATION_ROADMAP.md`、`docs/ML_AGENT_RESEARCH_100_SOURCES.md`、`docs/RESEARCH_SYNTHESIS.md`、`docs/RESEARCH_READING_LOG.md`、`docs/GITHUB_CONNECTION_TROUBLESHOOTING.md`；另讀 `docs/AGENT_RUN_STATE.md` 和 `docs/AGENT_LESSONS.md`。
1. 立刻核對最新main、PR、Actions job/log；舊 `startup_failure` 只是歷史。優先看P0–P2真實命題與兩份Word交付障礙，不靠反覆讀文獻取代核心功能。
2. baseline記SHA、失敗案例與實際分子分母；每輪只選**一項**可回退低風險改進，放候選分支／PR並查CI。沒故障證據不重做相同patch，未提交patch不可冒稱修好repo；正式版／封存集不得改。
3. 工具回 `This tool call was blocked by OpenAI's safety checks. Please double check what you are sending.` 即記完整原文、停止同寫入重試，分類平台安全阻擋；不猜Billing Lock、403、runner或pytest。
4. 分別報A程式回歸、B端到端、C獨立專家新題、D真實考生、E維運安全成本，記版本、prompt、模型／資料、token／費用／延遲（未知寫未知）、commit／rollback；G3≠G4≠G5≠G6。
5. 不阻礙交付時，最多詳讀3個未詳讀100來源索引條目；要讀可取得正文、日期、URL、深度、限制、改進。沒有專家盲審不能報90%，沒有考生資料不能算心理計量。
6. 實際完成後更新 `docs/AGENT_RUN_STATE.md`；明確且可核實的使用者回饋整理入 `docs/AGENT_LESSONS.md`，不存個資／秘密／封存答案，也不得覆蓋正式政策。
**完成**：可核對新commit/CI/真交付，或明確的可重現阻礙與下一個安全動作。無新證據不空轉。
