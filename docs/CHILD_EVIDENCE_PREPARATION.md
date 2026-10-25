# 兒少命題來源：先獨立取得，再執行本機模型

本工具解決「尚未安裝 Ollama 就無法檢查官方臨床來源是否可取得」的順序阻礙。它**不需要 Ollama**，不下載模型、不命題、不產生 Word、不呼叫付費 API。

在已安裝專案 Python 相依套件、可連上官方 NICE 網站的電腦執行：

```bash
python -m src.prepare_child_evidence --items 20 --out output/child-evidence.json
```

成功時只產生一份來源摘錄 JSON，含官方來源網址、擷取時間與原頁雜湊；已存在的檔案不會覆寫。若任一必要來源因 HTTP 403、連線或內容解析失敗，**不會發布部分檔案**。這不是免費模型推論成功，也不是臨床主張的獨立查證。

待使用者自己的電腦具備已安裝的免費本機模型後，才可執行：

```bash
python -m src.child_exam_pipeline --probe-local-inference --model qwen2.5
python -m src.child_exam_pipeline --evidence output/child-evidence.json --model qwen2.5 --items 20 --out output/child-docx
```

這樣可以把「官方來源能否讀取」與「本機模型能否推論」分別檢查，避免同一故障被誤判。指定其他題數時，準備來源和命題的 `--items` 應保持一致。來源摘錄僅是候選證據，不能代替逐題來源支持、臨床專家驗證或兩份 Word 首次可下載交付驗收。請勿把下載的來源全文或包含敏感資料的 JSON 提交至公開 repo。
