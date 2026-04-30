# Chapter 04 — Case: BigQuery pipeline

A real-world BigQuery pipeline plan: take an event stream from
PostgreSQL, dedup it into BigQuery, then fill in `checkout` events
that didn't make it across from the mobile client. It's written the
way a PM might propose it on a Monday — sensible-looking, organised,
with monitoring and rollout sections. It also has 7 hidden flaws,
spanning all 5 dimensions of the frame from chapter 2.

## Files

- [`plan.md`](./plan.md) — the design under review (no spoiler
  comments)
- [`ddl/events_raw.sql`](./ddl/events_raw.sql) — staging table DDL
- [`ddl/events_dedup.sql`](./ddl/events_dedup.sql) — target table DDL
- [`pipeline.sql`](./pipeline.sql) — Step C dedup + Step D imputation
- [`run-redteam.sh`](./run-redteam.sh) — runs the red team and writes
  to a timestamped output directory
- `expected-findings.md` — actual findings from the Day 4 canonical
  run, with the metadata header

## How to run

```bash
cd 04-case-bq-pipeline
bash run-redteam.sh
# → ./out-<timestamp>/ranked.md
```

Cost: about $0.30 per run (3 model calls, plus consolidation and
ranking).

## What this case demonstrates

The plan in `plan.md` looks like reasonable PM output: schema is
partitioned, the SQL has `GROUP BY`, monitoring is mentioned, dedup
logic is laid out. A single-LLM review will catch some of the issues
but miss others. Run the red team, then compare the consensus
findings (≥ 2 teams agreed) against the unique findings (only 1
team caught it). The unique ones are where the value compounds.

The 7 deliberately seeded flaws, in plain English:

- **A hidden assumption about which `source_event_id` survives the
  dedup.** The SQL pairs `MIN(event_ts)` with
  `ANY_VALUE(source_event_id)`. The writer probably assumed the
  surviving id would be from the earliest event. But `ANY_VALUE`
  means BigQuery can return any of them — the survivor is
  non-deterministic.
- **A SQL semantic issue in the imputation subquery.** The
  `NOT EXISTS` correlated subquery has unqualified column references
  (`WHERE m2.user_id = user_id`), so the inner query may not bind
  to the outer query the way the writer intended.
- **A boundary issue with imputed timestamps.** The synthetic
  `checkout` event is inserted at `MIN(event_ts) + 1 second`. That
  can land in a different daily partition than the real events, or
  collide with another real event recorded at the same second.
- **Postgres-to-GCS export ignores in-flight transactions and
  timezone semantics.** A row that's mid-transaction at the export
  cutoff, or a Postgres server in a non-UTC timezone, can quietly
  drop or double-count rows in BigQuery.
- **A misuse path:** if Step D is rerun without first re-running
  Step C, it silently creates duplicate imputed rows. Nothing in
  the plan prevents this.
- **A rollback gap.** There's no `imputation_run_id` or `loaded_at`
  on the dedup table, so there's no clean way to selectively undo
  a bad imputation deploy.
- **A monitoring ambiguity.** The plan says "alert if today's row
  count is less than 50% of expected." But what's "expected" — a
  rolling average? A fixed value? Week-on-week? Each interpretation
  has different failure modes.

The point isn't that this plan is *bad* — it's that even a sensible
plan has 7 problems a single-LLM review would miss. Multi-model
surfaces them.

## After your first run

The first time you run `run-redteam.sh`, an `out-<timestamp>/`
directory is created. Pick the run you trust most, then:

1. `cp out-<timestamp>/consolidated.md expected-findings.md`
2. Add the metadata header from
   [`../examples/expected-findings-template.md`](../examples/expected-findings-template.md)
   (run date, model versions, CLI versions)
3. Commit `expected-findings.md` so future readers can compare
   their runs against yours

The `out-<timestamp>/` directory itself is gitignored (per the root
`.gitignore`). Only the curated `expected-findings.md` is tracked.

[← Back to README](../README.md) · [中文版](./README.zh-TW.md)
