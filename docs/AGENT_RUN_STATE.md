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


## 2026-11-22｜來源語意與解析一致性修正（候選；以本節覆蓋上方過期阻礙快照）

- **更新的正式基準**：main仍為 `b7604d3d45d8e6f16cdcf96a21e03211e6519c3b`；本輪只更新 Draft PR #46，未合併、未改formal-v1.0／原核可題目。
- **已解除的遠端G3/傳輸障礙**：owner主動觸發 main 手動 run [45029306126](https://github.com/lily4318/clinical-psych-exam-agent/actions/runs/45029306126)，job `137229131237` success；真正本地Ollama `qwen2.5:3b` 命題甲乙各3題、驗證兩個非空DOCX、建立GitHub Draft Release `454489764`、遠端重新下載兩檔並 `cmp -s` 通過。兩檔38,507與38,769 bytes；**這不是ChatGPT首次雙附件G4，也不是獨立專家G5**。
- **本輪新失敗案例**：使用者貼出上述測試卷的第2題解析，NICE CG128 §1.5.1 的 `within 3 months` 被模型說成「至少在3個月後」，且A–D選項正誤標籤不同、實質理由相同。這是**使用者提供的文字證據**；本輪沒有下載二進位DOCX獨立鑑別其完整題幹和選項，故正解B仍待核對。來源正文已核對 https://www.nice.org.uk/guidance/cg128/chapter/Recommendations 。
- **根因蒸餾**：來源摘錄存在/來源ID合法不代表來源支持試題主張；答案位置由程式預先規劃，模型可能為符合字母要求硬湊理由；之前檢查只要求選項、解析非空且形式不同，沒有測量正解與錯誤選項是否有實質差異。之前的DOCX G3只查結構，非臨床正確性。
- **本輪唯一改善（來源與選項推理一致性關卡）**：於候選 `src/child_exam_pipeline.py` 加入簡潔來源時間方向／逐選項推理提示；在產檔前拒絕「正誤不同但相同理由」及已辨識的 `within N`→「至少N後」正解解析顛倒；補7個合成回歸測試 `tests/test_child_semantic_consistency.py`，`exam-compose` 技能要求先查來源時點量詞否定，再判正解，合併共同**錯誤**理由僅為待實作呈現規格。教訓見 `docs/AGENT_LESSONS.md`。
- **證據／候選commits**：初始 `019587673`（上輪348 passed），本輪程式 `098a9c3`、穩健處理 `9aadec7`、測試 `eeb81b9`、技能 `3c8861b`、測試fixture修正 `7e70196`；對應 pytest [run 45033586792](https://github.com/lily4318/clinical-psych-exam-agent/actions/runs/45033586792) job `137242298401` 原始日誌 `355 passed in 8.58s`。中途測試fixture缺 `equivalence_note` 導致1 fail/354 pass，已修正；不得把該短暫CI紅燈歸因為模型問題。
- **品質界線／下一障礙**：目前是**有限特徵的確定性哨兵**，不具完整跨語言來源語意蘊涵能力，也未驗證新模型生成成功率；需補實際真模型再命題與人工抽查，並於**保留A–D機器可驗證資料**前提下另行讓DOCX匯出器／驗證器支援相同錯誤理由合併。若任何選項正確性仍與來源不符，不可用排版整併掩蓋。
- **五軌（本次訓練）**：A=355/355 pytest（合成+結構回歸，非臨床）；B=歷史main遠端3/3+3/3 DOCX及下載成功，新提示後模型端到端成功數未知／未測；C=獨立專家0/0；D=真實考生0/0；E=本輪未新增付費服務，模型token與推論金額未知，新測試CI約8.58秒（非生成延遲）。版本：V2 Draft PR #46；模型實測歷史 `qwen2.5:3b`，本次訓練未呼叫模型。
- **回退方式**：只revert候選PR #46本輪程式／測試／技能／教訓／狀態提交或直接關閉Draft PR；main、formal-v1.0及正式藍圖不受影響。


## 2026-11-22 23:00｜真模型回歸新失敗（診斷紀錄；尚未修復）
- 最新 PR #46 head `6282948b71d51173b952b0dd22b484b577cf2cca`，仍 open/draft、未合併；main正式政策優先。
- 同一 head 的 pytest [run 45033747531](https://github.com/lily4318/clinical-psych-exam-agent/actions/runs/45033747531)，job `137242790187` 原始日誌 `355 passed in 4.94s`；這不是模型品質證據。
- **真實 Ollama 回歸失敗**：[run 45033747552](https://github.com/lily4318/clinical-psych-exam-agent/actions/runs/45033747552)，job `137242859509`。免費本地 `qwen2.5:3b` 已完成 P01–P03 的 A/B 六次真推論，但 `P03 form_b` 於輸出前被新語意哨兵拒絕：`Rationale contradiction: correct and incorrect options share the same substantive explanation after verdict labels are removed.`；exit code 1，**本次無兩份DOCX G3成功**。容器仍運作，OOMKilled=false，未見記憶不足訊號；故障類別是模型輸出品質／內容一致性拒絕，**不是**runner、Docker、付費API或平台安全拒絕。
- 本輪可驗證改善：將新真模型失敗的原始 run/job、確切拒絕原因、模型和完成範圍寫入跨對話狀態，避免後續把「pytest綠燈」誤判為端到端成功；**未修改產題程式、未重新觸發模型、未宣稱修復**。下一個工程單元應在候選分支加入**有上限的單題重生與重驗**，保留原始拒絕紀錄並測試重試耗時／終止條件；不能放寬哨兵或以假題替代。
- 五軌：A=355/355 pytest；B=本次真模型端到端0/1次成功（六次推論完成但驗證拒絕，G3未達）；C=0/0無獨立專家；D=0/0無考生；E=未使用付費API，六次推論耗時約689秒（各次118.9、110.3、80.1、80.9、150.6、148.2秒），token/金額未知；回退為 revert 本段狀態紀錄 commit 或關閉 Draft PR，main/formal未變。


## 2026-11-23 00:55｜單題重試後的真模型新障礙（候選診斷）
- Baseline：Draft PR #46 head `68fce107e15d676cbd2157c996d51a7ab46012a0`，open/draft、未合併；main `b7604d3d45d8e6f16cdcf96a21e03211e6519c3b`，正式 formal-v1.0 不變。
- 新增單題語意重試程式與測試的 PR pytest [45041657042](https://github.com/lily4318/clinical-psych-exam-agent/actions/runs/45041657042)，job `137267223598`，原始日誌確認 **356/356 passed in 8.68s**。這只驗證程式回歸，不等於真模型端到端成功。
- 同一 head 真實免費本地 Ollama `qwen2.5:3b` [45041657038](https://github.com/lily4318/clinical-psych-exam-agent/actions/runs/45041657038)，job `137267247366` **failed**：`ValueError: P07: duplicate question stem in 乙卷; already used by 乙卷 P01.`；生成失敗，DOCX verification skipped，沒有本次雙 Word 交付。容器 running=true、OOMKilled=false、記憶不足訊號未見。故障分類為跨題題幹重複（模型輸出品質／去重重試未恢復），不是 CI、runner、OOM、付費服務或安全攔截。
- 本輪唯一可回退改進：將最新原始失敗與明確的下一優先障礙持久化，避免再次針對已解除的 rationale contradiction 重複修改。尚未修改命題程式、未重新執行推論、未達 G3/G4。下一工程單元：在不放寬來源、語意與跨題去重驗證下，針對 P07 重試失敗設計可驗證的多樣化題幹約束／有限重生，先做合成測試，再跑真模型；仍失敗須拒絕輸出。
- 五軌 KPI：A=356/356；B=本次真模型端到端0/1，G3=0/1、G4未知；C=0/0（無專家資料）；D=0/0（無考生資料）；E=未呼叫付費 API，模型 token／成本未知，真模型整體耗時與逐次 token 未核實。rollback：revert 本次狀態 commit 或關閉候選 PR；不得合併 main。


## 2026-11-23 03:56｜語法修復後真模型新阻礙（原始日誌）
- Baseline：Draft PR #46 head `9ccbfeeceffbbd7eea87c4e6f188d84a95154d52`，open/draft，base main `b7604d3d45d8e6f16cdcf96a21e03211e6519c3b`；正式 formal-v1.0 不變。
- P0 修復確認：pytest [45058575272](https://github.com/lily4318/clinical-psych-exam-agent/actions/runs/45058575272)，job `137319183665` 原始日誌 `356 passed in 8.11s`，先前 SyntaxError 已解除。
- 真模型 [45058575277](https://github.com/lily4318/clinical-psych-exam-agent/actions/runs/45058575277)，job `137319183616` **failed**。免費 CPU Ollama `qwen2.5:3b` 的 P01 甲卷第一次推論 127.1s（prompt 2300/output 409 tokens），有限重生第二次 115.9s（2386/458 tokens），仍被拒絕：`P01 form_a: Rationale contradiction: correct and incorrect options share the same substantive explanation after verdict labels are removed.`。未開始有效乙卷／八配對交付，DOCX 檢查 skipped。容器 running=true、OOMKilled=false、記憶不足訊號未見；分類為**有限重生後內容語意一致性仍失敗**，不是語法／runner／OOM。
- 本輪可回退改進僅為新故障與兩次真推論成本的持久化，**未修改產題程式、未修復模型輸出、未完成 G3/G4**。下一工程單元應針對正誤選項解析共用理由，檢視 P01 生成提示和來源命題約束，設計一個具測試的最小改進；不能放寬語意哨兵或增加無界重試。
- 五軌 KPI：A=356/356；B=本次真模型端到端0/1，G3=0/1，G4=未驗證；C=0/0獨立專家；D=0/0真實考生；E=未使用付費模型 API，兩次推論合計243.0s，prompt tokens=4686，output tokens=867（僅本次 P01 A 兩次），完整成本未知。回退：revert 本段紀錄 commit 或關閉 Draft PR；不修改 main/formal。


## 2026-11-23 05:02｜真模型八配對首次 G3 成功（新證據，非 G4）
- Baseline：PR #46 head `790412f281b4d88f23fd400abd03d45280633bd7`，open/draft、未合併；正式 main/formal-v1.0 未變。本輪先重新讀取正式政策、任務書、狀態與教訓，並檢查原始 Actions job/log。
- P0：pytest [run 45063661959](https://github.com/lily4318/clinical-psych-exam-agent/actions/runs/45063661959)，job 137334931928，原始日誌 **356 passed in 8.51s**。
- **P2 重大新證據**：真實免費本地 Ollama `qwen2.5:3b` [run 45063661960](https://github.com/lily4318/clinical-psych-exam-agent/actions/runs/45063661960)，job 137334931977，原始日誌 `GENERATION_OUTCOME: success`、`VERIFICATION_OUTCOME: success`；甲乙各 **8 題**，各卷 answers=8、complete_option_rationales=8、reader_layout=modern_strict、errors=[]。兩份 DOCX 在 runner 上已實際生成並通過結構檢查，SHA256 分別 `1a41f35cc8707d1145bc95c1ebd1e337b6adc4471c5f91852be41dbc94945486` 與 `e1edbc03411515bbfdfdf9f818a02c3f9e7e85c244cd55967de5ccebb95513f4`。
- **不可擴大宣稱**：workflow 明示不儲存 artifact、不自動發布，runner 暫存檔在 job 結束清除；因此 **G3=1/1、G4=未驗證／未交付下載**。8 題成功不代表預設20題、成人領域、臨床語意支持、獨立專家品質或甲乙心理計量等值已通過。成功不是本輪新增程式造成；本輪僅將新驗證證據持久化。
- 下一個第一障礙：在不新增付費服務、保護個資與未經核可正式題的前提下，設計可驗證且安全的兩份 DOCX 下載交付路徑；應先釐清現有 runner 無 artifact 的限制，並做受控 G4 測試，不能以成功 job URL 冒充 Word 下載連結。
- 五軌：A=356/356；B=本次真模型8組配對生成+兩份 DOCX 結構驗證 1/1（G3），聊天端可下載 G4=0/0 未測；C=0/0；D=0/0；E=未使用付費 API，CPU 推論，完整 token、費用與總耗時本輪未彙整（未知）；rollback：revert 本段狀態紀錄，候選 PR 保持 draft，main/formal 不變。
