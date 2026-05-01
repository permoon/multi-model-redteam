# 5 點失敗維度紅隊框架

`multi-model-redteam` 的方法論核心。請先讀
[`../prompts/system-prompt.md`](../prompts/system-prompt.md) 了解 prompt 本身；
本檔解釋**為什麼**它長這樣。

## 5 個維度

紅隊 review 必須涵蓋全部 5 個。每個維度要求至少 2 個具體失敗劇本 — 抽象建議
（「加 monitoring」）會被明確拒絕。

### 1. 隱性假設（Hidden assumptions）

設計**隱含**依賴什麼，但沒寫出來？

常見軸：
- **順序**：訊息按發送順序到達、job 按提交順序執行
- **唯一性**：ID 不重複、名稱不衝突
- **原子性**：`read → modify → write` 是一個 step
- **資料新鮮度**：cache 是 coherent、replica 已同步
- **呼叫方行為**：呼叫方會 retry、呼叫方遵守 contract

### 2. 依賴失敗（Dependency failures）

當上下游依賴 degrade 時會壞什麼？

跟「downtime」不同 — degraded 表示**部分能用**：
- 5 分鐘 outage（用 retry 處理）
- 5 小時 outage（用 backpressure 或 human 升級處理）
- p99 latency 是平常 10 倍（timeout 連鎖）
- 間歇性 5xx error（retry storm 風險）

### 3. 邊界輸入（Boundary inputs）

p99 跟 malicious-percentile input 下會怎樣？

- 空輸入
- 單元素輸入
- 巨大批次（10× p99）
- Malformed（截斷、編碼壞）
- Malicious（刻意 weaponized）
- Adversarial timing（譬如分鐘邊界 burst）

### 4. 誤用路徑（Misuse paths）

如果人不照 plan 走會怎樣？三個子情境：
- **呼叫方** 行為錯誤：未來 PR 把 API wire 錯
- **使用者** 行為：end user 跳步驟、太快 retry 等
- **Operator** 行為：SRE 水平擴展、CI 一小時部署 5 次

### 5. 回滾與爆炸半徑（Rollback & blast radius）

怎麼救？傷害多大？

- **回滾流程**：誰跑什麼命令、多少時間
- **爆炸半徑**：影響多少 user / server / region
- **Detectability**：5 分鐘 alert，還是 5 天 silent corruption?
- **Reversibility**：資料 corruption vs config glitch

## 為什麼是這 5 點，不是 OWASP / SRE

| 框架 | 焦點 | 為什麼不用 |
|---|---|---|
| OWASP Top 10 | 安全漏洞 | 太窄 — 漏掉 ops 與資料 |
| SRE Four Golden Signals | 運維健康（latency / traffic / errors / saturation）| 只在 deploy **之後**有用；design review 需要 deploy **之前**的 lens |
| **5 點失敗維度** | **Deploy 前的 design review** | **針對部署前的 ops / data / IAM 失敗模式，這是上面兩個 frame 容易漏掉的層次** |

5 個維度是 code 完成跟 deploy 之間最常被漏掉的東西。等 SRE signal 噴的時候，
設計已經在 production。

## 校準：bad prompt vs good prompt

❌ **Bad prompt**（多數人最先試的寫法）：

> Review 這個設計，告訴我哪裡可能出錯。

這會產出「加 monitoring」、「用 retry」、「考慮 edge case」— 抽象建議，無法執行。

✅ **Good prompt**（本 repo 的框架）：

> 5 dimensions × ≥ 2 concrete scenarios each × {TRIGGER, IMPACT, DETECTABILITY}
> Reject abstract. Specify metric / threshold / alert.

這份 prompt 強迫模型：
1. **覆蓋全 5 維度**（不能挑簡單的）
2. **具體**：每劇本要有可重現的 trigger
3. **嚴重度推理**：detectability 隱含 SLO 思維

## 好 finding vs 壞 finding

| 維度 | 🔴 Bad finding（抽象、不可行動）| 🟢 Good finding（具體、可執行）|
|---|---|---|
| 隱性假設 | "Design assumes user_id is unique." | "Design assumes user_id stays unique across PostgreSQL → BQ migration. If a user is deleted then re-registered, BQ dedup silently merges old + new identity. TRIGGER: re-registration. IMPACT: cross-identity data bleed. DETECTABILITY: outlier query on score distribution — months." |
| 依賴失敗 | "API might fail." | "Vertex AI batch API has 60s p99 latency in `us-central1`; this Workflow has 30s timeout, so 5–10% of imputation calls fail silently. TRIGGER: any batch > 200 events. IMPACT: imputation skip without alert. DETECTABILITY: downstream coverage check — days." |
| 邊界輸入 | "Big batches might break." | "BigQuery INSERT has implicit row size limit; if any single user has > 50k events in 24h (bot/scrape), dedup INSERT fails and whole day's imputation rolls back. TRIGGER: 0.01% of days. IMPACT: 24h data loss. DETECTABILITY: Workflow alert — minutes." |
| 誤用路徑 | "User might call wrong order." | "Step C (dedup) and Step D (imputation) are independent BQ jobs. If operator manually re-runs Step D after Step C failed, imputation runs on stale data. TRIGGER: operator manual rerun. IMPACT: silent data bloat. DETECTABILITY: weekly QA query." |
| 回滾 / 爆炸半徑 | "Need to handle errors." | "Imputation has no `imputation_run_id` column; if logic ships buggy, rollback = `DELETE WHERE is_imputed = TRUE` for the day, which collides with future re-runs. TRIGGER: imputation regression. IMPACT: 1-day data loss + 30 min/incident manual recovery. DETECTABILITY: rare." |

規則：**好 finding 可以寫成 ticket** — PM 一看就知道要做什麼。壞 finding 是 vibe。

## 10 分鐘校準 rubric

模型產出 finding 後，每個都過這份 checklist。**5 個都打勾 = MUST-FIX 候選。
< 4 個打勾 = 拒絕並重寫**。

- [ ] 具體 TRIGGER（不是「if something goes wrong」）
- [ ] 具體 IMPACT（誰、多嚴重、可量化）
- [ ] 具體 DETECTABILITY（時間單位：分鐘 / 小時 / 天 / 永遠）
- [ ] 不是 generic advice（無「加 monitoring」/「用 retry」/「consider X」）
- [ ] 可寫成 ticket（PM 一看知道要做什麼）

這份 rubric 在嚴重度排序**之前**跑（[Chapter 06](../06-going-further/) 處理嚴重度）。
在這裡濾掉壞 finding 省 reviewer 時間。

## 常見陷阱

- **想擴張到 7 / 8 維度**：誘惑大但抗拒。先用現在 5 個跑 20 個案例；如果真的需要
  第 6 個（如「合規」對受監管產業），再加。不要預先 bloat 框架
- **LLM 預設給 generic advice**：prompt 中「Reject abstract. Specify metric /
  threshold / alert」這句是必要的。拿掉後輸出品質立刻塌
- **不要心算 rubric**：寫個小 script 用 pattern match 抓「加 monitoring」/
  「consider X」並 flag 那些 finding 重寫。Rubric 自動化才最有價值

## 這個框架的由來

這個框架是我（Hector）在 ValueX 跑了約 15 個 BigQuery pipeline 跟 GCP deploy
設計文的 multi-LLM review 後得到的版本。早期版本有 7 個維度（合規 + observability
是分開的）；我 collapse 它們因為總是跟既有 5 個 co-occur。如果你的領域真的需要
分開，fork prompt — 它是 CC0 license 就是為了這個。

[← 回到章節 README](./README.zh-TW.md)
