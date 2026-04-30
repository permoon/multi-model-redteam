# Chapter 02 — The 5-prompt frame

This chapter is the methodology core of the whole repo. Everything
else builds on the structure described here. Worth reading slowly —
or twice, if you came here from chapter 1 already convinced.

## Files

- [`frame.md`](./frame.md) — the full essay: why these five
  dimensions, how to calibrate findings, what makes a finding good
  vs bad, and a 10-minute rubric for triaging
- The prompt itself sits at
  [`../prompts/system-prompt.md`](../prompts/system-prompt.md) (CC0)

## What you walk away with

1. **Why** these 5 dimensions catch what OWASP / SRE checklists miss
2. **How** to recognise a bad finding ("add monitoring" with no
   thresholds) and reject it
3. A **rubric** for triaging findings before they hit severity
   ranking

## TL;DR

The frame asks, for any design, AT LEAST 2 concrete failure scenarios
across each of these five dimensions:

1. **Hidden assumptions** — ordering, uniqueness, atomicity, data
   freshness, caller behavior
2. **Dependency failures** — what happens when upstream / downstream
   services degrade or go down
3. **Boundary inputs** — empty, single, huge batch, malicious,
   malformed
4. **Misuse paths** — caller / user / operator using it the wrong way
5. **Rollback & blast radius** — how do you recover, and how big is
   the damage if it goes wrong?

Every scenario must include TRIGGER, IMPACT, and DETECTABILITY.
Generic advice like "add monitoring" is rejected outright — if you
can't say what metric, what threshold, what alert, the finding isn't
ready.

[`frame.md`](./frame.md) has the full reasoning behind each
dimension, calibration examples, and the 10-minute rubric.

[← Back to README](../README.md) · [中文版](./README.zh-TW.md)
