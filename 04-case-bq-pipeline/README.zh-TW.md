# Chapter 04 — 案例：BigQuery pipeline

一份真實的 BigQuery pipeline plan：把 PostgreSQL 的 event stream
dedup 進 BigQuery，再對沒從 mobile client 過來的 `checkout` 事件做
補值。整份 plan 寫得像 PM 週一早上提的那種 — 看起來合理、結構工整、
有 monitoring、有 rollout 計畫。但它也藏了 7 個漏洞，剛好涵蓋
chapter 2 框架的 5 個維度。

## 檔案

- [`plan.md`](./plan.md) — 被 review 的設計（**不**含 spoiler 註解）
- [`ddl/events_raw.sql`](./ddl/events_raw.sql) — staging table DDL
- [`ddl/events_dedup.sql`](./ddl/events_dedup.sql) — target table DDL
- [`pipeline.sql`](./pipeline.sql) — Step C dedup + Step D imputation
- [`run-redteam.sh`](./run-redteam.sh) — 跑紅隊，寫到 timestamped
  資料夾
- `expected-findings.md` — Day 4 canonical run 的實測 finding（含
  metadata header）

## 怎麼跑

```bash
cd 04-case-bq-pipeline
bash run-redteam.sh
# → ./out-<timestamp>/ranked.md
```

費用：每次約 $0.30（3 個 model call + consolidation + ranking）。

## 這個案例展示什麼

`plan.md` 看起來就是合理的 PM 產出：schema 有分區、SQL 有
`GROUP BY`、有提 monitoring、dedup 邏輯有寫。單一 LLM review 抓得
到一些東西、但會漏一些。跑完紅隊後比較 consensus（≥ 2 家同意的）
跟 unique（只有 1 家抓到的）— unique 那邊才是價值會 compound 的
地方。

7 個刻意藏起來的漏洞，用白話講是這樣：

- **隱性假設：dedup 後留下的 `source_event_id` 是哪一筆？** SQL 把
  `MIN(event_ts)` 跟 `ANY_VALUE(source_event_id)` 配在一起。寫的人
  大概以為留下來的會是最早那筆的 id。但 `ANY_VALUE` 意思是 BigQuery
  可以挑任何一筆 — 留誰是不確定的。
- **SQL 語意問題：imputation 子查詢有 alias shadowing。** `NOT
  EXISTS` 子查詢的 column reference 沒有 qualify（`WHERE
  m2.user_id = user_id`），所以內層查詢可能根本沒有綁到外層查詢預
  期的 user_id。
- **邊界問題：imputed timestamp 跨 partition 邊界。** 合成的
  `checkout` 事件被插在 `MIN(event_ts) + 1 秒`。這可能會落到跟真
  實事件不同的日 partition，也可能跟那一秒剛好有的真實事件撞時間
  戳。
- **依賴問題：PostgreSQL → GCS export 忽略 in-flight transaction
  與時區語意。** 一筆 export 切點時剛好在 transaction 中間的 row、
  或者 Postgres server 不是 UTC，都會讓 BigQuery 那邊靜默漏算或重
  複算。
- **誤用路徑：** Step D 沒先重跑 Step C 就單獨重跑，會悄悄產生
  duplicate imputed row。Plan 沒有任何地方擋住這件事。
- **回滾 gap。** Dedup 表上沒有 `imputation_run_id` 或 `loaded_at`，
  所以一個 imputation deploy 出問題時，沒辦法乾淨地只撤銷壞的那
  批。
- **Monitoring 模糊。** Plan 上寫「當天 row count 低於預期 50%
  時發 alert」。但「預期」是什麼基準 — 滾動平均？固定值？週對
  週？每種解讀有不同的失敗模式。

重點**不是**這份 plan 寫得爛 — 而是即使是合理的 plan，仍然有 7 個
單一 LLM review 看不見的問題。Multi-model 能把它們抓出來。

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
