# Chapter 04 — 案例：BigQuery pipeline

> 🚧 建構中 — Day 4 用實測產出（非預測）。

## 你會看到

一個真實的 BigQuery 設計：把 PostgreSQL 的事件流 dedup 進 BigQuery，再對中間缺漏
事件做補值。Plan 故意藏 7 個漏洞，跨 5 個維度。三家 LLM 各自抓不同 coverage；
其中一個漏洞**三家都漏**（人工發現的）。

## 檔案（完成後）

- `plan.md` — 被 review 的設計（**不**含 spoiler 註解）
- `ddl/` — 表結構 DDL
- `pipeline.sql` — 設計提案的實際 SQL
- `run-redteam.sh` — 對此案例跑紅隊
- `expected-findings.md` — Day 4 實測輸出，含 metadata header（model 版本、
  跑日期等），讓讀者可比對

[← 回到 README](../README.zh-TW.md)
