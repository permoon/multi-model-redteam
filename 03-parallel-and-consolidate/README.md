# Chapter 03 — Parallel + consolidate + rank

Three mini-lessons in one chapter, three scripts. Together they reproduce
[`final/redteam.sh`](../06-going-further/final/redteam.sh) — but each
script is small enough to read in 5 minutes and modify on its own.

## Mini-lessons

| Lesson | Script | Input | Output | Failure mode |
|---|---|---|---|---|
| 3a Parallel | [`03a-parallel.sh`](./03a-parallel.sh) | `plan.md` + `system-prompt.md` | `out/{claude,codex,gemini}.md` + `out/manifest.json` | < 2 teams succeed → abort |
| 3b Consolidate | [`03b-consolidate.sh`](./03b-consolidate.sh) | the 3 team outputs | `out/consolidated.md` | missing files auto-skip; need ≥ 2 |
| 3c Rank | [`03c-rank.sh`](./03c-rank.sh) | `consolidated.md` | `consolidated-ranked.md` | missing input → abort |

## Running them in sequence

From this chapter directory:

```bash
bash 03a-parallel.sh ../examples/sample-plan.md
bash 03b-consolidate.sh
bash 03c-rank.sh
```

The three scripts are deliberately decoupled — you can swap step 3b
(consolidator) or 3c (ranker) for a different model without touching the
parallel runner. To use Codex as the consolidator instead of Claude:

```bash
REDTEAM_CONSOLIDATOR="codex exec --skip-git-repo-check" bash 03b-consolidate.sh
```

## What you'll learn

### `bash &` + `wait` for true parallelism

Three sequential calls take ~85s on the sample plan. Three parallel calls
take ~57s (the slowest model dictates total time, which is Claude in our
data). That's ~1.5–2.4× speedup depending on which model is slow that
day. Bash gives you this for free; no orchestration framework needed.

### Why bash arrays don't work across subshells

A natural-looking implementation tries to update a parent-shell array
from background jobs:

```bash
declare -A STATUS
run_team() { ...; STATUS[$name]=ok; }    # ← runs in subshell
run_team claude "..." &
wait
echo "${STATUS[claude]}"                  # ← always empty!
```

The `&` puts `run_team` in a subshell. Subshells get a *copy* of the
parent's variables. Updates never propagate back. The script appears to
work in the loop, then mysteriously reports "0 teams succeeded" after
`wait`.

This bug was caught during plan v3 review. The fix is in `03a-parallel.sh`:
each team writes a `$name.status` file, and the parent reads them after
`wait`. File-based status crosses subshell boundaries cleanly.

### Consolidator as a 4th LLM call

The three raw outputs can disagree on findings, mostly agree but use
different wording, or duplicate the same finding three ways. `diff` and
`awk` can't merge by *meaning* — they merge by string. So we use a
fourth LLM call with a strict output schema:

- **Consensus** (≥ 2 teams)
- **Unique** (1 team — could be insight OR blind spot of others)
- **Apparent disagreements** (humans must resolve)
- **Coverage gaps** (which dimensions had thin coverage)
- **Triple blind spot** (consolidator's own observation, conservative)

See [`../prompts/consolidation-prompt.md`](../prompts/consolidation-prompt.md)
for the exact instructions.

### Severity ranking that doesn't drown in must-fix noise

LLMs trend conservative — left alone, they'll mark 15 things as MUST-FIX
on a 50-line plan. The severity prompt caps MUST-FIX at 5 unless the
design is broken at architecture level. See
[`../prompts/severity-prompt.md`](../prompts/severity-prompt.md).

## Why these are not in `final/redteam.sh`

[`final/redteam.sh`](../06-going-further/final/redteam.sh) is the
production version: 100 lines, all three steps in one file, manifest +
graceful degradation. **It's the script you actually run.**

These three scripts are the **teaching version** — split for clarity.
Once you understand them, you can read `final/redteam.sh` in one pass.

[← Back to README](../README.md) · [中文版](./README.zh-TW.md)
