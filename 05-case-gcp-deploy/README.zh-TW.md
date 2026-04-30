# Chapter 05 — 案例：GCP Cloud Run 部署

一份真實的 Cloud Run + Cloud Workflows 部署 plan，服務叫
`news-fetcher`（Node.js Express app，從 RSS feed 抓文章；每小時
batch fan-out + 偶爾的 ad-hoc request）。寫得像一個工程師第一天
提案 GKE → Cloud Run 遷移的樣子 — 看起來合理，config yaml、IAM、
region 都列了。但它藏了 7 個漏洞，跨 IAM、region、reliability、
reproducibility 等面向。

## 檔案

- [`plan.md`](./plan.md) — 被 review 的設計（**不**含 spoiler 註解）
- [`cloudrun.yaml`](./cloudrun.yaml) — Cloud Run service config
- [`workflows.yaml`](./workflows.yaml) — Cloud Workflows 編排
- [`iam.yaml`](./iam.yaml) — IAM bindings
- [`run-redteam.sh`](./run-redteam.sh) — 跑紅隊，寫到 timestamped
  資料夾
- `expected-findings.md` — Day 5 canonical run 的實測 finding（含
  metadata header）

## 怎麼跑

```bash
cd 05-case-gcp-deploy
bash run-redteam.sh
# → ./out-<timestamp>/ranked.md
```

費用：每次約 $0.30（3 個 model call + consolidation + ranking）。

## 這個案例展示什麼

這份 plan 表面看起來合理：yaml 結構完整、IAM 有指派服務帳號、region
有列、monitoring 有提、migration 還有 fallback。單一 LLM review 抓
得到一些、會漏一些。跑完紅隊比較 consensus（≥ 2 家同意）跟 unique
（只有 1 家抓到）— unique 那邊才是價值會 compound 的地方。

7 個刻意藏起來的漏洞，白話講是這樣：

- **IAM 範圍決策。** `news-fetcher-sa` 被綁到 `roles/editor` — 整
  個 project 等級的權限。實際只需要讀 Firestore、發 Pub/Sub。萬一
  服務被攻破，`roles/editor` 讓攻擊者可以刪 Firestore、推 image
  到 Artifact Registry、改 Pub/Sub 設定。應該綁特定 role 就好。
- **Region locality 問題。** Cloud Run 在 `us-central1`、Workflows
  在 `us-east1`。每小時 invocation 都吃跨 region latency 跟 egress
  費用。要不就是沒人注意到，要不就是有人以為 Workflows 會自己挑
  region（並不會）。
- **環境硬編碼。** `cloudrun.yaml` 裡面寫死
  `FIRESTORE_PROJECT=my-prod-project`。同一份 yaml 部署到 staging，
  staging 服務就會寫到 prod 的 Firestore。PII / 計費風險。
- **Reliability gap。** Workflows 那邊只有一個 `http.post` step，
  沒有 `retry` block。一次 transient HTTP 失敗（或 Cloud Run cold
  start 超過 workflow 預設 HTTP timeout）就丟掉整個小時的新聞抓
  取。
- **Latency SLO 衝突。** `minScale: 0` 跟 95% < 500ms 的 latency
  目標互斥。Idle scale-down 後，Cloud Run 在 Node.js 上的 cold
  start 通常要 2-5 秒。所以每小時 batch 的第一個 request 必定爆
  SLO。
- **Rollback 策略 gap。** Plan 裡沒提到 revision pinning、traffic
  split、或 bad deploy 的回退程序。Fallback 寫的是「GKE 那邊保
  warm」 — 但沒有 traffic 路由計畫，根本切不回去。
- **Reproducibility 問題。** Image 用 `:latest`。重新部署會抓當下
  被 tag 成 latest 的那一份，不是你驗證過的那一份。沒有方法可以
  「回到昨天那個版本」。

重點**不是**這份 plan 寫得爛 — 而是即使是合理的 plan，仍然有 7 個
單一 LLM review 看不見的問題。Multi-model 能把它們抓出來。

不同 model 在這種情境下有不同的擅長：Gemini 通常抓 GCP-native
pattern（region、IAM、服務行為）；Claude 通常抓 operational gap
（retry、rollback、監控閾值）；Codex 通常抓通用 anti-pattern
（`:latest`、hardcoded config）。Consensus + unique 的對比正好把
這些盲點和各家貢獻顯示出來。

## 第一次跑完之後

第一次跑 `run-redteam.sh` 會產生一個 `out-<timestamp>/` 資料夾。挑
你最信任的那次跑的結果，然後：

1. `cp out-<timestamp>/consolidated.md expected-findings.md`
2. 加上
   [`../examples/expected-findings-template.md`](../examples/expected-findings-template.md)
   的 metadata header（跑的日期、model 版本、CLI 版本）
3. Commit `expected-findings.md`，讓之後的讀者可以拿他們的 run 跟
   你的對

`out-<timestamp>/` 資料夾本身被 root `.gitignore` 排除 — 只有
curated 過的 `expected-findings.md` 進 git tracking。

[← 回到 README](../README.zh-TW.md) · [English](./README.md)
