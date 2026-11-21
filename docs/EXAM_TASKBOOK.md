# V2｜成果導向任務書（候選）
原始方法：描述「目標、做完長什麼樣、流程、使用者必要動作」，不把每個小步都變成人工確認。政策以 START_HERE、simulation_policy、release manifest 為準。

## 任務 A：一句話命題並交付甲乙 DOCX
**自然語言輸入**：「幫我做兒童版考卷」「兒童版10題」「成人版考卷」。未指定題數預設**每卷20題**，明示N則**甲乙各N題**。兒童版是臨床心理師國考程度的兒少領域考題。

**交付契約**：兩個不同、可開啟的Word，第一次最終回覆就提供「下載甲卷 Word」「下載乙卷 Word」可用連結。試題區只有題幹與A–D；各卷末尾順序為「命題範圍與依據→答案一覽→每題正解＋A/B/C/D逐項解析→來源對照→一行未經獨立專家驗證限制」。

**自主執行**：讀canonical與狀態→讀動態近五年真實來源→建立該領域專屬基準／N題比例藍圖→核對真實可用零額外付費推論→單一Agent命甲乙→schema／來源／高風險內容查核→用確定性Python匯出→重新讀兩個DOCX及 `python -m src.verify_external_delivery form_a.docx form_b.docx --items N`（可執行時）→首次回覆附上真實檔案連結→記錄G3和G4。
**完成**：G3兩份文件均有效**且**G4首次回覆兩個檔案都可取得。缺任一項先說「Word 尚未交付」，不宣稱完成。新草稿無需逐題人工核可，正式formal改版須明確核可。使用者只在登入、許可、正式發布、必要資源或不可合理預設的關鍵決策時介入。

## 任務 B：每小時或手動「繼續訓練」
**目標**：解除妨礙真實命題／兩份Word交付的首要障礙，每輪最多一個有證據的可回退改進；不是讀書量或patch數量。
**自主執行**：重讀 START_HERE、release/current_release、simulation_policy、ml_evaluation_policy、LONG_TERM_EVALUATION_ROADMAP、ML_AGENT_RESEARCH_100_SOURCES、RESEARCH_SYNTHESIS、RESEARCH_READING_LOG、GITHUB_CONNECTION_TROUBLESHOOTING，並核對main／PR／最新Actions jobs及原始log；先取baseline SHA與失敗案例→擇P0–P2一項最小可逆改進→候選分支／PR→實際查CI→回寫進度、五軌KPI及rollback。
**故障**：安全拒絕直接記原文，不繞過重試；pytest trace屬程式錯誤；沒模型是推論可用性；G3與G4不同；無專家／真實考生資料就不能報品質或心理計量達標。無新證據停止空轉。研究僅在不阻礙交付時最多詳讀3篇索引來源，註URL／日期／閱讀深度／限制／具體改進。
**完成**：新可驗證交付／候選變更＋CI／精確當前阻礙之一。未提交本機patch不能叫修好repo，不直接修改main或正式版本。
