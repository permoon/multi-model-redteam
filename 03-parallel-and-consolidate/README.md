# Chapter 03 — Parallel + consolidate + rank

Three mini-lessons in one chapter. Three small scripts. Together
they reproduce
[`final/redteam.sh`](../06-going-further/final/redteam.sh) — but
each script is small enough to read in 5 minutes and modify on its
own.

## Mini-lessons

| Lesson | Script | Input | Output | Failure mode |
|---|---|---|---|---|
| 3a Parallel | [`03a-parallel.sh`](./03a-parallel.sh) | `plan.md` + `system-prompt.md` | `out/{claude,codex,gemini}.md` + `out/manifest.json` | Fewer than 2 teams succeed → abort |
| 3b Consolidate | [`03b-consolidate.sh`](./03b-consolidate.sh) | the 3 team outputs | `out/consolidated.md` | Missing files auto-skip; need ≥ 2 |
| 3c Rank | [`03c-rank.sh`](./03c-rank.sh) | `consolidated.md` | `consolidated-ranked.md` | Missing input → abort |

## Run them in order

From this chapter's directory:

```bash
bash 03a-parallel.sh ../examples/sample-plan.md
bash 03b-consolidate.sh
bash 03c-rank.sh
```

The three scripts are deliberately decoupled. You can swap step 3b
(the consolidator) or 3c (the ranker) for a different model without
touching the parallel runner. For example, to use Codex as the
consolidator instead of Claude:

```bash
REDTEAM_CONSOLIDATOR="codex exec --skip-git-repo-check" bash 03b-consolidate.sh
```

## What you'll learn

### `bash &` + `wait` for real parallelism

Three sequential calls take about 85 seconds on the sample plan.
Three parallel calls take about 57 seconds. The slowest model
dictates total wall time, which in our data is usually Claude. So
you get a 1.5–2.4× speedup depending on which model is slow that
day. Bash gives you this for free. No orchestration framework
needed.

### Why bash arrays don't survive a subshell

The natural-looking implementation tries to update a parent-shell
array from background jobs:

```bash
declare -A STATUS
run_team() { ...; STATUS[$name]=ok; }    # ← runs in subshell
run_team claude "..." &
wait
echo "${STATUS[claude]}"                  # ← always empty!
```

`&` puts `run_team` in a subshell. Subshells get a *copy* of the
parent's variables. Updates never propagate back to the parent. The
script looks fine inside the loop, then mysteriously reports "0
teams succeeded" after `wait`.

This bug got caught during plan v3 review. The fix lives in
`03a-parallel.sh`: each team writes its result into a `$name.status`
file, and the parent reads those files after `wait`. File-based
status crosses subshell boundaries cleanly.

### The consolidator is a 4th LLM call

The three raw outputs can disagree on findings, agree but use
different wording, or describe the same finding three different
ways. `diff` and `awk` can't merge by *meaning* — they merge by
strings. So we use a fourth LLM call with a strict output schema:

- **Consensus** (≥ 2 teams agree)
- **Unique** (1 team only — could be that team's insight, or could
  be the other two's blind spot)
- **Apparent disagreements** (humans need to resolve these)
- **Coverage gaps** (which dimensions had thin coverage)
- **Triple blind spot** (what the consolidator thinks all three
  missed; conservative)

The exact instructions are in
[`../prompts/consolidation-prompt.md`](../prompts/consolidation-prompt.md).

### Severity ranking that doesn't drown in must-fix noise

Left alone, LLMs trend conservative. They'll mark 15 things as
MUST-FIX on a 50-line plan. The severity prompt caps MUST-FIX at 5
unless the design is broken at the architecture level. See
[`../prompts/severity-prompt.md`](../prompts/severity-prompt.md).

## Why these aren't just `final/redteam.sh`

[`final/redteam.sh`](../06-going-further/final/redteam.sh) is the
production version: 100 lines, all three steps in one file,
manifest plus graceful degradation. **It's the script you actually
run.**

These three scripts are the **teaching version** — split for
clarity. Once you understand them, the production script reads in
one pass.

[← Back to README](../README.md) · [中文版](./README.zh-TW.md)
