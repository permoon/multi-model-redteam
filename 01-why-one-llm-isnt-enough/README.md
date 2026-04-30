# Chapter 01 — Why one LLM isn't enough

You're using Claude Code (or Cursor, or Codex CLI) to review your code
already. It works pretty well. So why would you stack a second model on
top? Let alone a third?

The cheapest way to answer this is to just try it. Below is 28 lines
of Python with 5 bugs hidden in it. You'll run Claude on it, run Codex
on it, then read both reviews side by side. Takes about a minute, costs
about two cents. By the end you'll see the answer for yourself.

## Files

- [`target-code.py`](./target-code.py) — 28 lines of Python with 5
  bugs hidden in it. The bugs are listed below in this README, not in
  the code itself, so the models can't cheat.
- [`compare-models.sh`](./compare-models.sh) — runs Claude, then runs
  Codex, on the same code. Saves both reviews to
  `review-claude.md` / `review-codex.md`.

## Run it

```bash
cd 01-why-one-llm-isnt-enough
bash compare-models.sh
# → review-claude.md
# → review-codex.md
```

Cost: about $0.02. Two short calls on a 28-line file.

## What's in the code

It's an "order scoring batch" — for each event, it dedups by user,
writes a score row to SQLite, and pushes a running loyalty total to
some downstream API. Looks fine at a glance. Has 5 problems.

1. **Dedup uses `user_id` only.** The same person placing two
   different orders looks like a duplicate, so the second one gets
   dropped. Quietly. Nothing logs it. That order just disappears.
2. **SQL injection.** The `INSERT` line builds the SQL by f-string
   concatenation. Pass in `e['user_id']` like `Robert'); DROP TABLE
   scores;--` and you've got a textbook SQL injection. (Bonus: if
   `score` is non-numeric, the quoting breaks too.)
3. **Floating-point drift in `total`.** Each event adds `score * 0.1`
   to `total`. Computers can't represent 0.1 exactly, so across
   thousands of events that small error stacks up. After enough
   events, `total` won't match what you'd get re-computing it from
   scratch. Whether that matters depends on what `total` is for. If
   it's loyalty points: probably fine. If it's reconciling against
   a finance system: not fine.
4. **Retries with no backoff, 10 in a row.** When the downstream API
   is genuinely broken, this code fires 10 immediate retries per
   event. So you're hammering a service that's already on fire.
   Exactly the opposite of what you should be doing.
5. **`conn.commit()` is outside the loop.** If the script crashes at
   event 9,999 of 10,000, none of those 9,999 events are saved.
   You start over from zero. Real systems commit per event, or in
   checkpoints, so partial progress survives a crash.

## What you'll see

LLM output is non-deterministic, so your runs won't be identical to
ours. But run it a few times and the rough pattern looks like this:

| Bug | Claude alone | Codex alone |
|---|---|---|
| 1. Dedup key | usually catches | sometimes catches |
| 2. SQL injection | catches | catches |
| 3. Float accumulation | sometimes catches | rarely catches |
| 4. Retry, no backoff | catches | sometimes catches |
| 5. Commit outside loop | sometimes catches | usually catches |

The pattern, after a few runs:

- **One model alone catches 3 of the 5.** Sometimes 4. Rarely all 5.
- **Two models together catch 4 or 5.** But which one each model
  contributes is not stable across runs.
- **They have different personalities.** Claude tends to over-warn
  (it'll suggest extra defensive checks that aren't strictly bugs).
  Codex is shorter and more matter-of-fact, and sometimes skips
  bug #3 or #4 entirely.

The point isn't that Claude is better than Codex or the other way
around. The point is: **one review is one sample of a noisy
process**. Two samples already shifts the picture. Three (next
chapter) shifts it more.

## So why not stop at two?

Two models still share a lot of the same blind spots. They've all
learned from overlapping pools of text on the internet. When they
both miss something, they tend to miss the *same* thing. And when
they both agree, there's no third voice to break the tie.

There's also a scale thing going on here. This chapter is small on
purpose: 28 lines, 5 bugs, easy to grasp. But the real-world plans
that need this method aren't 28 lines. They're an architecture, a
pipeline design, a deploy strategy. That's where having a third model
matters most, and where one-line bugs aren't really the issue
anymore.

[Chapter 2](../02-the-five-frame/) introduces the prompt structure
that makes the third model add real findings instead of more
text. Chapters 4 (BigQuery pipeline) and 5 (Cloud Run deploy) put
the full method on real engineering plans and show you how much
further it goes.

[← Back to README](../README.md) · [中文版](./README.zh-TW.md)
