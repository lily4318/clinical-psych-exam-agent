# V2｜跨對話工作狀態（候選）
此檔是**任務進度快照**，不是正式版本：正式版本唯讀 `release/current_release.yaml`；每次對話重查GitHub才可稱為最新。

- 記錄：2026-11-21 Asia/Taipei；基準 `main@b7604d3d45d8e6f16cdcf96a21e03211e6519c3b`。
- 本輪查得開啟PR：0；Actions歷史成功run `40833369315`，job `123312407353` 原始log `341 passed in 6.56s`（2026-10-29，非新pytest）。
- `formal-v1.0`、核可題目與正式藍圖維持不變。
- 核心阻礙：尚無 owner-only `manual_child_draft_release.yml` 自main手動 `items=3` 真實遠端雙DOCX發布／重新下載成功證據；甲乙20+20真模型吞吐及跨平台G4仍未證實。
- 本輪唯一候選改進：V2單核心＋四程序技能＋任務書＋狀態／學習紀錄＋靜態路由測試；候選分支 `refactor/agent-operating-model-v2-20261121`，Draft PR #46 已建立；初版候選 commit 80ee80611ab69c6e6c2a15f551a466501c82bbc6 的 PR pytest run 44914301797／job 136876501186 原始日誌確認 344/344 通過。此狀態檔更新將另產生後續 commit／CI，須重新核對；不得以既有成功冒稱新 commit 已驗證。
- 本輪模型推論／來源盲測／專家新題／真實考生試驗：未新增。token／推論費用／延遲：未知；未使用付費API。

## 五軌KPI：請勿混用
| 軌道 | 本輪證據 |
|---|---|
| A程式回歸 | 歷史341/341；候選CI待查 |
| B Agent端到端 | 新遠端首次雙Word trial 分子／分母未有正式驗證；不能把缺測當成功 |
| C專家新題 | 0/0（尚無評分，比例未定義） |
| D真實考生 | 0/0（未收集，心理計量不可算） |
| E維運／安全／成本 | 無新付費服務；token／成本未知；回退為關閉候選PR並保留main |

## 實際完成後更新欄位
`trial_id / 台灣日期時間 / baseline SHA / candidate commit+PR+run+job / 任務與N題 / 資料、來源、藍圖、prompt、模型版本 / 本輪唯一修改 / 五軌分子分母 / G3與G4與G5與G6的獨立證據 / token、成本、延遲（未知寫unknown）/ 原始失敗及分類 / 可自主下一步／必要人工動作 / rollback`。
不存密碼、金鑰、病人個資、封存評測答案。狀態過期須重新查核，沒有新證據不反覆覆寫檔案。
