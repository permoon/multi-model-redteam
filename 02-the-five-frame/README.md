# Chapter 02 — The 5-prompt frame

The methodology core of `multi-model-redteam`. Read this chapter twice
before moving on.

## Files

- [`frame.md`](./frame.md) — full essay on the 5 dimensions, why these
  five, calibration, good vs bad finding, the 10-minute rubric
- The prompt itself is at [`../prompts/system-prompt.md`](../prompts/system-prompt.md) (CC0)

## What you'll walk away with

1. **Why** the 5-dimension frame catches what OWASP / SRE miss
2. **How** to spot a bad finding ("add monitoring") and reject it
3. A **rubric** to triage findings before they reach severity ranking

## TL;DR for the impatient

The frame demands, for every design, AT LEAST 2 concrete scenarios across
each of:

1. **Hidden assumptions** — ordering, uniqueness, atomicity, freshness, caller behavior
2. **Dependency failures** — upstream / downstream degradation patterns
3. **Boundary inputs** — empty, huge, malformed, malicious
4. **Misuse paths** — caller / user / operator getting it wrong
5. **Rollback & blast radius** — how to recover, scope of damage

Each scenario must include TRIGGER, IMPACT, DETECTABILITY. Generic advice
("add monitoring") is explicitly rejected.

Read [`frame.md`](./frame.md) for why each dimension exists, calibration
examples, and the 10-minute rubric.

[← Back to README](../README.md) · [中文版](./README.zh-TW.md)
