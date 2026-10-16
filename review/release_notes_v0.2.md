# Review Release v0.2

日期：2026-10-16  
狀態：待複核  
使用者最終核可：否

## 版本目的

此版本建立在 `review-v0.1` 的內容正確性、來源與平行卷 reviewer 基礎上，再加入「考生視角」審查：刻意只看題幹與選項，不依賴解析與來源，檢查實際作答難度、關鍵字送分、雙答案、正解長度線索與過度明顯的干擾選項。

唯一 canonical 組卷入口為 `review/release_manifest_v0.2.yaml`。

包含批次：

- P01–P04：`pilot_p01_p04_v0.2.json`
- P05–P08：`pilot_p05_p08_v0.3.json`
- P09–P12：`pilot_p09_p12_v0.3.json`
- P13–P16：`pilot_p13_p16_v0.2.json`
- P17–P20：`pilot_p17_p20_v0.3.json`

## 本輪考生視角修訂

### P07｜耐受性／戒斷

舊版只需看到「需要更高劑量」或「停酒後顫抖」即可作答，實際難度低於中等。

v0.3 改為：

- 甲卷加入醫療監督下 opioid 使用，要求辨識耐受性，同時避免把耐受性單獨等同 OUD。
- 乙卷同時呈現酒精戒斷與再次飲酒降低不適，要求區分 withdrawal 與 negative reinforcement。

### P09｜AVE 與復發歷程

舊版仍可由題幹中的全盤失敗語句直接對應 AVE。

v0.3 要求考生進一步理解：

- lapse 不等於必然完整 relapse；
- AVE 是 lapse 後的自我失敗歸因、羞愧／無望與低自我效能如何增加後續再使用風險；
- cue reactivity、negative reinforcement 與 tolerance 可參與復發，但不足以取代 AVE 對題幹歷程的解釋。

### P12｜戒癮藥物

舊版題幹直接提示「opioid receptor antagonist」，容易變成名詞配對。

v0.3 改為臨床條件判斷：

- OUD：完成解毒、無 opioid 生理依賴、希望每月一次非 agonist 長效治療，辨識 extended-release naltrexone。
- AUD：個案仍需 opioid 止痛藥，要求判斷 naltrexone 的 opioid blockade 與用藥安全考量。

並新增 `SAMHSA-NALTREXONE` 作為當前權威藥物來源。

### P17｜延宕折扣

舊版只有正解完整描述較陡延宕折扣，其餘選項過於容易排除。

v0.3 的干擾選項改為「部分正確＋過度推論」：

- 正確辨識較陡折扣，卻錯把它當成 SUD 特異診斷指標；
- 正確辨識較陡折扣，卻直接推論為單一多巴胺功能異常；
- 正確看到群體關聯，卻錯誤推論個體因果。

考生需同時掌握定義、研究關聯與推論邊界。

## 全卷難度判斷

- 基礎題 P01、P02：保留直接核心知識辨識。
- 中等題中保留少數中等偏易錨點（如 P06、P14），避免整份考卷所有中等題都變成高認知負荷的多步驟題。
- P03、P04、P07、P08、P11、P12、P14 等題形成從情境辨識到臨床應用的中等層次。
- P09、P13、P15、P16、P17、P18、P20 的實際推理負荷與進階／整合定位較一致。

## 預期全卷藍圖

每卷 20 題：A4／B3／C2／D4／E4／F3。  
難度：基礎2／中等11／進階7。  
認知層次：記憶2／理解8／應用7／整合3。  
答案位置：A、B、C、D 各 5 題。

## 組卷

```bash
clinical-psych-review-build
```

或：

```bash
python -m src.assemble_review_exam
```

預設使用 `release_manifest_v0.2.yaml`，通過硬性驗證後輸出至 `output/review-v0.2/`。

## CI 狀態

GitHub Actions 仍因此 private repository 的 runner 啟動環境在建立 job 前回傳 `startup_failure`，因此只保留手動 `workflow_dispatch`。不能把此狀態解讀為 GitHub runner 已執行並通過 pytest。

## 核可規則

此 release 仍為 `待複核`、`approved_by_user=false`。Agent reviewer、程式驗證與考生視角複核均不能取代使用者最終核可。
