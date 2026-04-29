# Chapter 05 — 案例：GCP Cloud Run 部署

> 🚧 建構中 — Day 5 用實測產出（非預測）。

## 你會看到

一個真實的 Cloud Run + Cloud Workflows 部署 plan，服務名稱 `news-fetcher`。
Plan 故意藏 7 個漏洞：IAM `roles/editor`、region mismatch（Cloud Run vs
Workflows）、`:latest` image tag、Workflows 沒設 retry 等。三家 LLM 各抓不同
子集 — Gemini 傾向抓 GCP 專屬陷阱、Claude 抓 rollback gap。

## 檔案（完成後）

- `plan.md` — 設計（**不**含 spoiler 註解）
- `cloudrun.yaml`、`workflows.yaml`、`iam.yaml` — 實際 config
- `run-redteam.sh`
- `expected-findings.md` — Day 5 實測輸出

[← 回到 README](../README.zh-TW.md)
