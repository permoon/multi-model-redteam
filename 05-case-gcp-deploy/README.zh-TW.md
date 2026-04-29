# Chapter 05 — 案例：GCP Cloud Run 部署

一份真實的 Cloud Run + Cloud Workflows 部署 plan，服務名稱 `news-fetcher`
（Node.js Express app，每小時 batch fan-out + ad-hoc request）。Plan 寫得像
一個工程師第一天提案 GKE → Cloud Run 遷移的樣子 — 看起來合理，藏了 7 個
漏洞，跨 IAM、region、reliability、reproducibility 等面向。

## 檔案

- [`plan.md`](./plan.md) — 被 review 的設計（**不**含 spoiler 註解）
- [`cloudrun.yaml`](./cloudrun.yaml) — Cloud Run service config
- [`workflows.yaml`](./workflows.yaml) — Cloud Workflows 編排
- [`iam.yaml`](./iam.yaml) — IAM bindings
- [`run-redteam.sh`](./run-redteam.sh) — 跑紅隊，輸出到 timestamped 資料夾
- `expected-findings.md` — Day 5 canonical run 的實測 finding（含 metadata header；第一次跑後產生）

## 怎麼跑

```bash
cd 05-case-gcp-deploy
bash run-redteam.sh
# → ./out-<timestamp>/ranked.md
```

成本：每次約 $0.30（3 個 model call + consolidate + rank）。

## 這個案例展示什麼

這份 plan 看起來像合理工程師產出：yaml 結構完整、IAM 有指派服務帳號、
region 有列、monitoring 有提、migration 有 fallback。單一 LLM review 會
抓到一些 issue 但漏掉一些。跑紅隊後比較共識 finding（≥ 2 家）跟獨家
finding（1 家） — 後者是價值 compound 的地方。

具體說，這個案例設計來 surface：

- 一個 **IAM 範圍決策**：`news-fetcher-sa` 拿 `roles/editor` 遠超實際需求
  （只需要 Firestore read + Pub/Sub publish）
- 一個 **region locality 問題**：Cloud Run 在 `us-central1`、Workflows 在
  `us-east1` — 每小時呼叫都吃跨 region latency + egress 費用
- 一個 **環境硬編碼**：`cloudrun.yaml` 裡 `FIRESTORE_PROJECT=my-prod-project`
  ，staging 部署會打到 prod Firestore
- 一個 **reliability gap**：Workflows 沒設 retry policy，一次 transient HTTP
  失敗（或 Cloud Run cold start 超過 OIDC call timeout）會丟一小時的新聞
- 一個 **latency SLO 衝突**：`minScale: 0` 加上 95% < 500ms 目標互斥 —
  Cloud Run 在 Node.js 上 idle scale-down 後 cold start 通常會超過 500ms
- 一個 **rollback 策略 gap**：沒提 revision pinning、traffic split、或回退
  bad deploy 的程序
- 一個 **reproducibility 問題**：`:latest` image tag 意謂重新部署可能拉到
  不同 binary；沒辦法 roll forward 到「昨天跑的那個版本」

重點**不是**這份 plan 寫得爛 — 而是即使合理的 plan，仍有 7 個單一 LLM
看不見的漏洞。Multi-model 能 surface 它們。不同模型有不同擅長：Gemini
傾向抓 GCP 原生 pattern（region、IAM）、Claude 傾向抓 operational gap
（retry、rollback）、Codex 抓通用 anti-pattern（`:latest`、hardcoded
config） — consensus + unique 的對比正好展示盲點。

## 跑完後

第一次跑 `run-redteam.sh` 會產生 `out-<timestamp>/` 資料夾。挑最信任的那次，
然後：

1. `cp out-<timestamp>/consolidated.md expected-findings.md`
2. 加上 [`../examples/expected-findings-template.md`](../examples/expected-findings-template.md)
   的 metadata header（run 日期、model 版本、CLI 版本）
3. Commit `expected-findings.md`，讓之後讀者可以對比

`out-<timestamp>/` 資料夾本身被 root `.gitignore` 排除 — 只有 curated 的
`expected-findings.md` 進 git tracking。

[← 回到 README](../README.zh-TW.md) · [English](./README.md)
