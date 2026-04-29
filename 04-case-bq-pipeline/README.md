# Chapter 04 — Case: BigQuery pipeline

> 🚧 Under construction — built on Day 4 (actual run, not synthetic).

## What you'll see

A real-world BigQuery design: dedup an event stream from PostgreSQL into
BigQuery, then impute missing intermediate events. The plan has 7 hidden
flaws spanning all 5 dimensions. Three LLMs find them with different
coverage; one of them gets missed by all three (humans found it).

## Files (when complete)

- `plan.md` — the design under review (no spoiler comments)
- `ddl/` — table definitions
- `pipeline.sql` — the actual SQL the design proposes
- `run-redteam.sh` — runs the red team on this case
- `expected-findings.md` — actual outputs from Day 4 run, with metadata
  header (model versions, run date, etc.) so readers can compare

[← Back to README](../README.md)
