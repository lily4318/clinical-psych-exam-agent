# V2｜高自主臨床心理命題 Agent 架構（候選）
建立：2026-11-21（Asia/Taipei）。狀態：候選，未部署、未證實端到端；不是底層模型權重訓練。

## 核心目標與移植方法
由 AI-Team-Camp v1.9.1 借鑑「總路由 → 任務書 → SKILL → 真實驗收 → 持久進度 → 反饋蒸餾」，**只移植方法，不移植行銷角色或系統**。一個核心臨床心理命題 Agent 配合 Python 確定性管線，接到一句自然語言指令便自行尋找來源、建該領域藍圖、真實命題、驗證及交付兩份 Word。只在必要登入／授權／重大決策時打斷使用者。專用規範名稱為「**命題規範與來源依據**」，不是品牌手冊。

## 權威來源及優先序
1. 零額外費用、資安、安全與必要人工授權；任何技能或學習回饋不得越權。
2. `release/current_release.yaml` 指向的 `formal-v1.0`、已核可題目／答案／正式藍圖及正式審核程序**不可改寫**。
3. `START_HERE.md`、`config/simulation_policy.yaml`、`config/ml_evaluation_policy.yaml`、`agent/system_prompt.md`、`docs/CROSS_PLATFORM_ACCEPTANCE.md` 等既有規範。
4. `AGENTS.md` 路由；唯一公開入口 `.agents/skills/clinical-psych-exam/SKILL.md`；下列四個子技能是**工作程序，不是四個獨立模型**。
5. `docs/EXAM_TASKBOOK.md` 定義完成條件；`docs/AGENT_RUN_STATE.md` 記進度；`docs/AGENT_LESSONS.md` 記證實回饋，不得覆蓋1–3。

GitHub 是持久狀態唯一來源；已刪除 Google Drive 不得假定還在。公開使用者以唯讀操作原作者 repo，若需持久個人修改先用 Fork。

## 模組分工與路由
| 用戶意圖 | 工作技能 | 必須完成 |
|---|---|---|
| 兒童／成人版、歷屆五年、來源、藍圖 | `exam-evidence-blueprint` | 動態索引最新五個可得年度；領域專屬藍圖／真實來源支持 |
| 命題、甲乙、N題、再出題 | `exam-compose` | 真正零額外費用模型推論；甲乙每卷預設20題或指定N題；A–D逐項解析與兩卷JSON |
| 輸出Word、交付、下載 | `exam-docx-delivery` | 兩份可開啟DOCX／每卷末尾答案解析／G3結構驗證與G4首次雙下載 |
| 繼續、卡住、訓練、每小時優化 | `exam-continuous-improvement` | 最新PR／Actions及原始日誌、每輪一項可回退實質改進、五軌KPI和記憶回寫 |

一鍵命題順序：`exam-evidence-blueprint → exam-compose → exam-docx-delivery`；不新增主管／修正／輸出等多個獨立Agent。審查Agent只在P3用20–50真實任務 A/B 比較錯誤漏判、誤判、來源支持、平行等值、完成率、延遲及成本有淨效益時才加入。

## 端到端狀態機
`requested → evidence_checked → blueprint_ready → genuine_generated_json → content_checked → docx_g3_verified → first_reply_g4_verified → draft_delivered`。

- 「兒童版」是兒少**臨床心理師國考領域**，不是給兒童作答。從 `data/historical_exam_index.csv` 動態解析最近五個可得考試年度；不能固定111–115。不可用物質濫用固定藍圖直接套兒少。指定N題需按領域基準比例縮放，不可截取前N題。
- `genuine_generated_json` 須有真實可用免費推論；Stub／FakeModel／固定合成題僅用於回歸測試。GitHub Actions免費runner不是免費LLM，禁止付費API、runner、微調或會產帳單的服務。
- `content_checked` 可包含schema／答案唯一性／來源ID／A–D逐項解析；診斷、藥理、答案與來源支持等高風險內容須查證，單Agent自評不是獨立專家驗證。
- `docx_g3_verified` 要重新開啟兩份真DOCX確認可讀、題數正確、末尾命題範圍、答案、正解及A–D解析、逐題來源。 `first_reply_g4_verified` 要**第一次最終回覆**有兩個實際可取得的下載連結，後補不倒算首次成功。
- `draft_delivered` 僅指「未經獨立專家驗證」草稿，不等於G5專家評分、G6真實考生心理計量，亦不改正式核可狀態。無法交付時首次回覆就寫「Word 尚未交付」。

## 跨對話狀態與學習
新對話先讀正式規範、`docs/AGENT_RUN_STATE.md`、`docs/AGENT_LESSONS.md`；立刻比對live main、PR、CI與任務狀態，再載入本輪需要的子技能，無需重問已知背景。每次**確實完成工作**才寫日期、任務、SHA、證據、已驗收狀態、阻礙、下一步及rollback。回饋只記使用者實際指示／有證據修正，超過20條蒸餾去重，不保存金鑰、病人資料或封存考題答案；學習紀錄不能覆蓋權威政策。

平台安全檢查回應 `This tool call was blocked by OpenAI's safety checks` 時記原文、停止同寫入重試，分類 `platform_safety_block`，不能推論Billing Lock、runner、403、branch protection或pytest。沒新失敗證據不要重做patch；缺模型不能假生成。

## 訓練與衡量方向
P0：免費PR pytest綠燈、隔離分支及rollback。P1：有效甲乙JSON→兩份真DOCX並驗證。P2：免費真模型／專屬來源與藍圖／短指令端到端。P3：20–50任務做單／雙Agent候選A/B。P4：≥100道未洩漏新題經獨立專家五項全合格率≥90%、零重大診斷藥理答案來源錯誤、報95%CI；尚未驗證不得宣稱達標。P5：有真實考生資料後才算難度、鑑別度、誘答、信度與實證等值。
五軌KPI分開：A程式回歸、B端到端、C獨立專家、D真實考生、E維運安全成本。各記分子分母、版本、模型、來源、prompt、token／費用（未知寫未知）、commit及rollback。封存集不可每小時調參，115年已使用題目只是歷史診斷。100筆研究索引不等於100篇全文；每輪最多3筆尚未詳讀正文，不能延後P0–P2交付。
