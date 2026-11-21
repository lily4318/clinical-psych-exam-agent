# V2｜跨對話工作狀態（候選）
此檔是**任務進度快照**，不是正式版本：正式版本唯讀 `release/current_release.yaml`；每次對話重查GitHub才可稱為最新。

- 記錄：2026-11-21 Asia/Taipei；基準 `main@b7604d3d45d8e6f16cdcf96a21e03211e6519c3b`。
- 本輪重新查得 Draft PR #46 仍 open、未合併，head `08718dc9cf8bcf03fe08a96600bbccf2899a31d1`；Actions歷史成功run `40833369315`，job `123312407353` 原始log `341 passed in 6.56s`（2026-10-29，非新pytest）。
- `formal-v1.0`、核可題目與正式藍圖維持不變。
- 核心阻礙：尚無 owner-only `manual_child_draft_release.yml` 自main手動 `items=3` 真實遠端雙DOCX發布／重新下載成功證據；甲乙20+20真模型吞吐及跨平台G4仍未證實。
- **2026-11-22 證據更正**：`docs/CROSS_PLATFORM_ACCEPTANCE.md` 已記載 2026-10-22 的甲乙各10題及 2026-10-25 的甲乙各20題 ChatGPT 冷啟動測試，使用者均確認首次回覆兩份 DOCX 可下載開啟（各 1/1）；另有 2026-10-21 修正後甲乙各3題的首次下載確認 1/1。這些是**歷史平台 G4 使用者確認成功**，不得再籠統寫「跨平台 G4 從未成功」。但原始 DOCX 未供獨立 G3 檢查、實際讀取的 repo SHA 與模型未知，且**不能證明目前 V2 候選管線、GitHub Draft Release 或其他平台 G4**。當前阻礙精確限定為「V2 新整合流程的遠端發布／首次雙下載尚無實測」。
- **2026-11-22 最新候選 CI**：PR #46 head `2ed821ff00ebdd9506b4c6ef52858eb7b243476a`，run [44938518849](https://github.com/lily4318/clinical-psych-exam-agent/actions/runs/44938518849)，job `136950406132`，原始日誌 `348 passed in 8.88s`。此為靜態／回歸證據，非 G3/G4 新成功。
- 本輪唯一候選改進：V2單核心＋四程序技能＋任務書＋狀態／學習紀錄＋靜態路由測試；候選分支 `refactor/agent-operating-model-v2-20261121`，Draft PR #46 已建立；初版候選 commit 80ee80611ab69c6e6c2a15f551a466501c82bbc6 的 PR pytest run 44914301797／job 136876501186 原始日誌確認 344/344 通過。第二次候選 head `08718dc9cf8bcf03fe08a96600bbccf2899a31d1` 的 Actions run `44914466917` 亦已完成 success；新增內容的 pytest 原始日誌為 `344 passed in 8.76s`。此狀態檔更新另產生後續 commit／CI，須重新核對，不得以舊 CI 冒稱新 commit 已驗證。
- 本輪模型推論／來源盲測／專家新題／真實考生試驗：未新增。token／推論費用／延遲：未知；未使用付費API。

## 本輪新核對的真實整合證據（2026-11-21，非本輪新模型推論）

- **2026-10-27 歷史真實整合成功**：GitHub Actions [run 40436488179](https://github.com/lily4318/clinical-psych-exam-agent/actions/runs/40436488179)、job `121966251665`，`real child pair to two DOCX diagnostic`，`main@e141daab26002814764cd9587fa5f69ae2c88e82`，實際使用本地免費 Ollama／qwen2.5:3b 推論。原始 job log 的 `verify_external_delivery` JSON 為 `ok: true`、`items_per_form: 8`，甲乙各8題、各8份答案及8題完整選項解析，錯誤與警告皆空。此為**真正模型推論＋runner內兩份DOCX G3成功**，不是 Stub；但 job log 明示 `host_download_links: not_verified_by_local_file_check`、`clinical_correctness_and_source_support: not_independently_verified`、`parallel_psychometric_equivalence: not_verified`。**不能推論 Draft Release 遠端發布、首次 ChatGPT G4 或 G5/G6 成功**。
- **2026-11-21 最新 V2 候選 CI 已完成**：Draft PR #46 head `3ab77ef7e4579608d2a5cad7059a1ea3150bd3c7`，Actions [run 44916906783](https://github.com/lily4318/clinical-psych-exam-agent/actions/runs/44916906783) `completed/success`、job `136884367102` `completed/success`。此結果僅屬 pytest 回歸；本輪尚未重新讀取該 job 原始測試總數，**不**將舊的344/344直接冒充本次 head 的數量。
- **本輪唯一修正**：將已經存在但未在跨對話狀態清楚記載的「真模型8+8 runner G3」與「尚無遠端 Draft Release/G4」分開入帳；並更新上一個 PR head 的 CI 由待查變為 success。這是證據分類修正，**未新增模型命題、未重跑推論、未啟動 owner-only dispatch、未改程式功能**。
- 回退：僅 revert 本次候選文件 commit；`main`、`formal-v1.0`、正式題目、來源、藍圖均未變動。

## 五軌KPI：請勿混用
| 軌道 | 本輪證據 |
|---|---|
| A程式回歸 | 歷史 main 341/341；V2 候選 head 08718dc 的 Actions 344/344（2026-11-21）；本次狀態修正後新 CI 待查 |
| B Agent端到端 | 新遠端首次雙Word trial 分子／分母未有正式驗證；不能把缺測當成功 |
| C專家新題 | 0/0（尚無評分，比例未定義） |
| D真實考生 | 0/0（未收集，心理計量不可算） |
| E維運／安全／成本 | 無新付費服務；token／成本未知；回退為關閉候選PR並保留main |


## 下一個真正的 P1／P2 驗收動作（非已完成）

1. 目前 main 已有 owner-only `.github/workflows/manual_child_draft_release.yml`，其 guard 限 `github.actor == 'lily4318'`、`github.triggering_actor == 'lily4318'`、`refs/heads/main`，只能由有權限的擁有者在 GitHub Actions UI 手動選 `items=3` 啟動；候選 PR **不可**代替這個授權動作。無授權時不要透過 API／token 模擬或重送 dispatch。
2. owner 啟動後，先查 workflow run/job 原始日誌是否完成 `Generate real source-grounded parallel forms`、`Verify exact two nonempty Word files`、`Publish only verified files`；後者會檢查 Draft Release 資產恰兩個、重新下載並 `cmp -s` 位元組相同。需回讀實際 run／release／資產，不可只看 green CI。
3. 這個 Draft Release 是 owner-visible 的 GitHub 資產，**不等於**一般使用者「第一次 ChatGPT 回覆提供兩個可下載 Word」的 G4；該平台 G4 須獨立實測與記錄首次回覆。先跑3+3診斷，再決定8+8、20+20吞吐測試，不能假定完成。
4. 沒有 owner 授權或模型可用性證據時，後續可自主改善新領域的來源、命題規格、確定性驗證與回歸；只在有可核對的變更與新證據時更新此狀態。不得把模擬 `fake gh` 傳輸測試算成真實遠端發布。

## 實際完成後更新欄位
`trial_id / 台灣日期時間 / baseline SHA / candidate commit+PR+run+job / 任務與N題 / 資料、來源、藍圖、prompt、模型版本 / 本輪唯一修改 / 五軌分子分母 / G3與G4與G5與G6的獨立證據 / token、成本、延遲（未知寫unknown）/ 原始失敗及分類 / 可自主下一步／必要人工動作 / rollback`。
不存密碼、金鑰、病人個資、封存評測答案。狀態過期須重新查核，沒有新證據不反覆覆寫檔案。
