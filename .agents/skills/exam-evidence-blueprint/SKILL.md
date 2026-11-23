---
name: exam-evidence-blueprint
description: 為兒少、成人等臨床心理師國考領域整理可查核來源、最近五個可取得考試年度與專屬考點藍圖；適用「來源、考點、兒童版、成人版、藍圖」。
---
# 命題規範與來源依據｜領域藍圖技能
先讀 `START_HERE.md`、`release/current_release.yaml`、`config/simulation_policy.yaml`、`agent/system_prompt.md`、`docs/AGENT_ARCHITECTURE_V2.md`。
1. 從 `data/historical_exam_index.csv` 解析最近**五個可取得**正式國考年度；不足五年照實記錄，年份不要永久寫死。
2. 兒童版是**兒童／青少年臨床心理領域**的臨床心理師國考程度；不得把既有物質濫用藍圖套用到新領域。新藍圖獨立儲存，正式 `config/blueprint.yaml`／formal不改。
3. 對每項核心考點建立 `來源ID、可核對網址／檔案位置、實際支持片段、閱讀深度、限制`。索引、摘要或不可取得正文不可當成全面查證；高風險診斷、藥理、答案與來源支持要逐一核查，不憑空補造。
4. 建該領域20題基準配置：考點、難度、認知層次與臨床推理；要求N題就依simulation_policy比例縮放／最大餘數法並記錄例外，不截取前N題。
**完成**：動態年份、專屬藍圖、實際來源支持及缺口可追溯；缺關鍵來源時如實停在尚未查證狀態，不假稱已完成命題。
