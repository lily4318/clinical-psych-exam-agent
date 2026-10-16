# Google Drive Source Repository

Google Drive 作為本 Agent 的原始資料庫；GitHub 作為正式版本庫與唯一正式設定來源（source of truth）。

## Google Drive 主資料夾

- 臨床心理師考題 Agent
- Folder ID: `12UhJJLMrqgZukdZpgAcoPaKwBDu8VEaY`

## 主要資料

### 系統規格與提示詞
- Google Doc ID: `1bwE9Zj0BxsDwXbP4Sql3SfKhQwfe8mF1rYFihWJoBI8`
- 原位置：`01_Agent規格與提示詞`

### 題庫與考點藍圖
- Google Sheet ID: `1LbJg71zex4LZNU_8W9anrx1s--R48a9k9NOSob3ZoU8`
- 原位置：`02_歷屆考題與知識來源`
- 重要分頁：`題庫`、`考點藍圖`、`甲乙卷配對`、`品質檢核`、`官方來源`

## 分工原則

GitHub 保存：
- system prompt
- 命題藍圖
- 歷屆考點索引
- 官方來源索引
- 平行題規格
- schema
- 品質檢核與程式碼

Google Drive 保存：
- 官方 PDF
- 教材與講義
- 參考文獻
- 大型或需人工閱讀的原始檔
- 工作中的表格與文件

## 同步原則

1. `config/blueprint.yaml` 與 `config/parallel_form_blueprint.csv` 為目前正式命題設定。
2. 若 Google Drive 舊工作表與 GitHub 設定衝突，以 GitHub `main` 分支為準，再決定是否回寫 Drive。
3. 2026-10-16 建立可執行版時發現舊 `甲乙卷配對` 的 P01–P20 認知層次合計為「記憶2／理解7／應用7／整合4」，與正式藍圖「記憶2／理解8／應用7／整合3」不一致。正式 GitHub 版已將 P09「失誤效應（AVE）與復發歷程」由「整合」調整為「理解」，保留 P20 作為 D 類整合題，使類別與整體認知層次配置一致。
4. 若 Google Drive 中的正式藍圖、歷屆索引或 Agent 規則有重大修改，應同步更新 GitHub 並留下 commit 紀錄。
