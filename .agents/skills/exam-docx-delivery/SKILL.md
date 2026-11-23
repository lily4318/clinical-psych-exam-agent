---
name: exam-docx-delivery
description: 將已查驗的甲乙JSON轉成兩個真DOCX，核對卷末逐項解析、來源對照與首次回覆雙下載；適用「Word、下載、交付」。
---
# DOCX交付與G3/G4獨立驗收
依 `START_HERE.md`、`docs/CROSS_PLATFORM_ACCEPTANCE.md`、`docs/EXAM_TASKBOOK.md`、`src/export_docx.py` 行事；不改已核可試題及正式版三檔輸出規則。
1. 輸入兩份非Stub的合法甲乙JSON及可驗證來源，預設每卷20或使用者指定每卷N題。
2. 兩份Word各自試題區只有題幹／A–D；卷末依序列「命題範圍與依據→答案一覽→每題正解與A/B/C/D逐項解析→逐題來源對照與參考資料→一句未經獨立專家驗證限制」。
3. 重新開啟確認檔案存在非空、可讀、兩卷不同、題數／選項／解析／來源完整；可用時執行 `python -m src.verify_external_delivery form_a.docx form_b.docx --items N`。兩卷都通過是**G3**，非臨床專業正確性。
4. **第一次最終回覆**提供真實可點取「下載甲卷 Word」「下載乙卷 Word」；以平台實際附件證據確認**G4**，不假造sandbox路徑或把GitHub程式網址當成下載。
5. 任一卷或首次連結無法取得時，第一次回覆寫「Word 尚未交付」及具體阻礙；追問補交不可倒算首次G4成功。草稿不等於G5專家、G6考生或正式核可。
**完成**：G3兩份通過**且**G4首次雙附件確實可取得，缺一不可。
