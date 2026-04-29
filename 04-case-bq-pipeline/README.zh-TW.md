# Chapter 04 — 案例：BigQuery pipeline

一份真實的 BigQuery pipeline plan：把 PostgreSQL 的 event stream dedup 進
BigQuery，再對缺漏的中間 `checkout` 事件做補值。Plan 寫得像 PM 第一天提案的
樣子 — 看起來合理，藏了 7 個漏洞跨 5 個維度。

## 檔案

- [`plan.md`](./plan.md) — 被 review 的設計（**不**含 spoiler 註解）
- [`ddl/events_raw.sql`](./ddl/events_raw.sql) — staging table DDL
- [`ddl/events_dedup.sql`](./ddl/events_dedup.sql) — target table DDL
- [`pipeline.sql`](./pipeline.sql) — Step C dedup + Step D imputation
- [`run-redteam.sh`](./run-redteam.sh) — 跑紅隊，輸出到 timestamped 資料夾
- `expected-findings.md` — Day 4 canonical run 的實測 finding（含 metadata header；第一次跑後產生）

## 怎麼跑

```bash
cd 04-case-bq-pipeline
bash run-redteam.sh
# → ./out-<timestamp>/ranked.md
```

成本：每次約 $0.30（3 個 model call + consolidate + rank）。

## 這個案例展示什麼

這份 plan 看起來像合理 PM 產出：schema 有 partition、SQL 含 `GROUP BY`、
有提 monitoring、dedup 邏輯有列。單一 LLM review 會抓到一些 issue 但漏掉一些。
跑紅隊後比較共識 finding（≥ 2 家）跟獨家 finding（1 家） — 後者是價值
compound 的地方。

具體說，這個案例設計來 surface：

- 一個 **隱性假設**：dedup 後哪一筆的 `source_event_id` 會留下來（搭配
  `MIN(event_ts)`）
- 一個 **SQL 語意問題**：imputation 子查詢的 alias shadowing（`NOT EXISTS`
  correlated subquery）
- 一個 **邊界問題**：imputed timestamp 可能跨 partition 邊界
- 一個 **依賴問題**：PostgreSQL → GCS export 忽略 in-flight transaction
  與 timezone 語意
- 一個 **誤用路徑**：沒先 re-run Step C 直接重跑 Step D 會 silently 製造
  duplicate
- 一個 **回滾 gap**：沒有 `imputation_run_id` 無法選擇性 undo 壞的
  imputation deploy
- 一個 **monitoring 模糊**：「< 預期 50%」— 預期是什麼基準（滾動平均、
  固定值、週對週）？

重點**不是**這份 plan 寫得爛 — 而是即使合理的 plan，仍有 7 個單一 LLM
看不見的漏洞。Multi-model 能 surface 它們。

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
