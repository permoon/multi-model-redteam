# Chapter 03 — Parallel + consolidate + rank

> 🚧 Under construction — built on Day 3.

Three mini-lessons in one chapter, three scripts:

| Lesson | Script | Input | Output | Failure mode |
|---|---|---|---|---|
| 3a Parallel | `03a-parallel.sh` | `plan.md`, `system-prompt.md` | `out/{claude,codex,gemini}.md`, `out/manifest.json` | < 2 teams succeed → abort |
| 3b Consolidate | `03b-consolidate.sh` | the three team outputs | `out/consolidated.md` | missing files auto-skip; need ≥ 2 |
| 3c Rank | `03c-rank.sh` | `consolidated.md` | `consolidated-ranked.md` | missing input → abort |

## What you'll learn

- Bash `&` + `wait` for true parallelism (~3× speedup vs sequential)
- Why bash array state can't cross subshells (and how to use status files
  instead)
- Using a 4th LLM call to consolidate — and why not to handle it manually
- Severity ranking that doesn't drown in must-fix noise

[← Back to README](../README.md)
