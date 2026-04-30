# Chapter 01 — Why one LLM isn't enough

You already use Claude Code (or Cursor, or Codex CLI) to review code.
It catches a lot of issues. So why bother with a second model — let
alone a third?

This chapter is the cheapest way to find out: 28 lines of Python with
5 deliberate flaws, two single-model reviews, side by side. Run it
yourself in 60 seconds.

## Files

- [`target-code.py`](./target-code.py) — 28-line Python script, 5
  deliberate design flaws (no spoiler comments — flaws are listed in
  this README, not in the code)
- [`compare-models.sh`](./compare-models.sh) — runs Claude then Codex
  sequentially, saves both reviews to `review-claude.md` /
  `review-codex.md`

## How to run

```bash
cd 01-why-one-llm-isnt-enough
bash compare-models.sh
# → review-claude.md
# → review-codex.md
```

Cost: ~$0.02 (two short calls on a 28-line script).

Then read both files and compare against the 5 expected flaws below.

## The 5 flaws hidden in `target-code.py`

The code is an "order scoring batch" — read events, dedup by user,
write a score row to SQLite, push a running loyalty total downstream.

1. **Dedup key only uses `user_id`** — the same user placing two
   different orders is treated as a duplicate; second order silently
   dropped.
2. **SQL injection via f-string** — `INSERT INTO scores VALUES
   ('{e['user_id']}', {e['score']})` is a textbook SQLi (plus a quoting
   bug if `score` is non-numeric).
3. **Floating-point error accumulates in `total`** — `total +=
   e["score"] * 0.1` runs across N events; IEEE-754 drift compounds.
   Whether it matters depends on what `total` is used for downstream.
4. **Retry without backoff, 10 attempts** — on a real downstream
   outage, this fires 10 immediate calls per event, amplifying load
   on the failing dependency exactly when you want to ease off.
5. **`conn.commit()` outside the loop** — if the process crashes
   mid-batch, every event processed since the start of the call is
   lost. Should be a per-event commit (or an explicit
   transaction/checkpoint strategy).

## What you'll observe

Output is non-deterministic, so your specific runs may differ. The
typical pattern across runs:

| Flaw | Claude solo | Codex solo |
|---|---|---|
| 1. Dedup key | usually catches | sometimes catches |
| 2. SQL injection | catches | catches |
| 3. Float accumulation | sometimes catches | rarely catches |
| 4. Retry no backoff | catches | sometimes catches |
| 5. Commit outside loop | sometimes catches | usually catches |

Run it twice or three times and you'll typically see:

- **Each model alone catches 3 out of 5.**
- **Together they catch 4 or 5 out of 5** — but the gap is rarely the
  same flaw twice in a row.
- **Each model has a stylistic bias** — Claude over-flags (suggests
  defensive checks that aren't strictly bugs); Codex stays terser and
  occasionally skips finding #3 or #4 entirely.

The takeaway isn't "Claude > Codex" or vice versa. It's that **a single
review is one sample from a noisy distribution**. Two samples already
shifts the picture; three (next chapter) shifts it again.

## So why not just stop at two?

Two models still share blind spots:

- Both are transformers trained on overlapping public corpora, so they
  often miss the same concurrency / consistency / IAM patterns
- When they agree, you have no third opinion to break the tie
- The asymmetry shows up most on **architecture-shaped** plans (this
  chapter is intentionally code-shaped to keep things small) — chapters
  04 and 05 use a real BigQuery pipeline and a real Cloud Run deploy
  to surface this

[Chapter 02](../02-the-five-frame/) introduces the prompt frame that
makes a third model add real signal instead of just more text.

[← Back to README](../README.md) · [中文版](./README.zh-TW.md)
