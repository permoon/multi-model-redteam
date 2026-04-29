# Chapter 04 — Case: BigQuery pipeline

A real-world BigQuery pipeline plan: dedup an event stream from
PostgreSQL into BigQuery, then impute missing intermediate `checkout`
events. The plan is written the way a PM might propose it on day one —
looks reasonable, but has 7 hidden flaws spanning all 5 frame dimensions.

## Files

- [`plan.md`](./plan.md) — the design under review (no spoiler comments)
- [`ddl/events_raw.sql`](./ddl/events_raw.sql) — staging table DDL
- [`ddl/events_dedup.sql`](./ddl/events_dedup.sql) — target table DDL
- [`pipeline.sql`](./pipeline.sql) — Step C dedup + Step D imputation
- [`run-redteam.sh`](./run-redteam.sh) — runs the red team, outputs to a timestamped dir
- `expected-findings.md` — actual findings from a Day 4 canonical run, with metadata header (created after first real run)

## How to run

```bash
cd 04-case-bq-pipeline
bash run-redteam.sh
# → ./out-<timestamp>/ranked.md
```

Cost: ~$0.30 per run (3 model calls + consolidate + rank).

## What this case demonstrates

This plan looks like reasonable PM output: schema is partitioned, SQL
includes `GROUP BY`, monitoring is mentioned, dedup logic is listed. A
single LLM review will catch some issues but miss others. Run the red
team and compare consensus findings (≥ 2 teams) against unique findings
(1 team) — the latter are where the value compounds.

Specifically, this case is designed to surface:

- A **hidden assumption** about which row's `source_event_id` survives
  dedup when paired with `MIN(event_ts)`
- A **SQL semantic** issue in the imputation subquery (alias shadowing
  in the `NOT EXISTS` correlated subquery)
- A **boundary** issue with imputed timestamps potentially crossing
  partition boundaries
- A **dependency** issue: PostgreSQL → GCS export ignores in-flight
  transactions and timezone semantics
- A **misuse** path: rerunning Step D without first re-running Step C
  silently creates duplicates
- A **rollback** gap: there's no `imputation_run_id` to selectively undo
  a bad imputation deploy
- A **monitoring** ambiguity: "less than 50% of expected" — expected by
  what measure (rolling average, fixed value, week-on-week)?

The point is **not** that this plan is bad — it's that even a sensible
plan has 7 invisible-to-one-LLM flaws. Multi-model surfaces them.

## When you've run it

The first time you run `run-redteam.sh`, an `out-<timestamp>/` directory
appears. Pick the run you trust most, then:

1. `cp out-<timestamp>/consolidated.md expected-findings.md`
2. Prepend the metadata header from
   [`../examples/expected-findings-template.md`](../examples/expected-findings-template.md)
   (run date, model versions, CLI versions)
3. Commit `expected-findings.md` so future readers can compare

The `out-<timestamp>/` directory itself is gitignored (per the root
`.gitignore`) — only the curated `expected-findings.md` is tracked.

[← Back to README](../README.md) · [中文版](./README.zh-TW.md)
