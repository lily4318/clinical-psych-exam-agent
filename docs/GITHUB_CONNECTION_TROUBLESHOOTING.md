# GitHub 連線與 Actions startup_failure：診斷、測試、處理
檢查日期：2026-10-18。

## 已查明的兩種不同障礙
A. **ChatGPT GitHub connector 正常**：此 repo 公開、connector 有 pull/push/admin 權限，已成功讀取多個檔案並以 connector 寫入 commit。無需重新連接帳號。
B. **隔離的程式執行環境 DNS 受限**：`git ls-remote https://github.com/lily4318/clinical-psych-exam-agent.git` 回傳 `Could not resolve host: github.com`。此隔離環境的 DNS/網路政策不等於使用者 Windows 電腦 DNS。此處無法以重設 GitHub PAT 或重連 connector 修復環境網路，須換能存取外網的 runner 或改用 GitHub connector 做內容讀寫。
C. **GitHub Actions 既有 67 個 runs**，最近失敗紀錄（2026-10-16）為 `startup_failure` 與 `BuildFailed`，其中檢查的一個 run jobs=0，顯示 job 根本沒啟動。不代表 pytest 程式本身失敗。2026-10-18 發現 repo 已轉為 public，轉公開後是否恢復要重新做手動 smoke run，不能由先前紀錄推斷。

## 請擁有者手動做一次最小化驗證（約5步）
1. 登入 GitHub，開啟 `https://github.com/lily4318/clinical-psych-exam-agent`。
2. 點 **Actions**。左側選 **GitHub Actions connectivity smoke test**。若看不到，確認 `main` 有 `.github/workflows/connectivity_smoke.yml`。
3. 點 **Run workflow**，Branch 選 **main**，再按綠色 **Run workflow**。
4. 點剛出現的執行紀錄：若 `smoke` job 綠勾，則 runner 成功啟動；再回 Actions 選 **tests**，執行 pytest workflow。不要先更改任何正式試題。
5. 若 `startup_failure`/ `BuildFailed` 再現且 jobs=0，至 **Settings → Actions → General** 檢查 **Actions permissions** 是否允許執行 GitHub 與第三方 Action 並儲存。再檢查個人帳號 **Settings → Billing and licensing / Plans and usage**；公開標準 GitHub-hosted runners 一般不計使用分鐘，但仍可能受帳號限制。此處不應建議盲目付費或建立高成本 runner。

若以上仍失敗：由 GitHub UI 的 **Support** 聯絡 GitHub 支援，附 repo URL、具體失敗 run URL、`startup_failure`、`BuildFailed`、jobs=0、已改 public 仍失敗等證據，請排查 repository/account workflow routing / runner provisioning。官方文件亦指出帳號控制的封鎖可能無法僅透過 repository 設定修復。

## Windows 本機若是另外出現 `Could not resolve host`
* 請先用瀏覽器嘗試 https://github.com ，再 PowerShell 執行 `nslookup github.com`。
* 若瀏覽器與 DNS 都失敗，檢查 VPN / proxy / 防火牆與 DNS；公司或校園網路可請管理員協助。
* 若本機瀏覽器正常，**不必因 ChatGPT 隔離環境 DNS 失敗而調整你本機網路**。
* 直接在自己的 Windows 執行 Git/pytest 也可以，但需先安裝 Python 與專案相依套件；切勿將 API keys 寫入公開 GitHub。

## 官方文件
- https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository
- https://github.com/github/docs/blob/main/content/billing/concepts/product-billing/github-actions.md
