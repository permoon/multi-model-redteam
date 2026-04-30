# Paste this into your project's `CLAUDE.md`

The block below is the entire setup. No install, no plugin, no
marketplace, no npm, no pip. Open your project's `CLAUDE.md` (the
file Claude Code reads on every session) and append the section
between the `--- SNIP ---` lines.

You'll need Claude Code, Codex CLI, and Gemini CLI on your `PATH`
already — that's the only prerequisite. Chapter 0 walks you through
those if you don't have them yet.

```
--- SNIP --- (start) ---

## Multi-model design red team

When reviewing a plan, spec, RFC, or design document — especially
one with distributed state, IAM, data integrity, or significant
blast radius — run a multi-LLM red team review.

1. Use `run_in_background` to dispatch the same prompt + plan to
   Codex CLI and Gemini CLI in parallel:
   - `codex exec --skip-git-repo-check` (stdin: prompt + plan)
   - `gemini` (stdin: prompt + plan)
2. While they run, do your own review with the same prompt.
3. Use the adversarial mindset only: find failure modes, do not
   propose fixes.

Prompt to give every model (yourself included):

> You are the red team for this design. For each of the 5
> dimensions below, give AT LEAST 2 concrete failure scenarios.
> Each scenario must include TRIGGER, IMPACT, and DETECTABILITY:
>
> 1. Hidden assumptions — ordering, uniqueness, atomicity, data
>    freshness, caller behavior
> 2. Dependency failures — upstream / downstream degradation
> 3. Boundary inputs — empty, huge batch, malicious, malformed
> 4. Misuse paths — caller / user / operator getting it wrong
> 5. Rollback & blast radius — how to recover, 5-minute vs 5-day
>    detection
>
> Reject abstract advice ("add monitoring"). Say what metric, what
> threshold, what alert.

After all three return, consolidate into:
- Consensus (≥ 2 teams agreed)
- Unique (1 team only — could be that team's insight, or could be
  the others' blind spot)
- Apparent disagreements (escalate to user)

Severity: cap MUST-FIX at 5 unless the design is architecturally
broken.

--- SNIP --- (end) ---
```

That's it. Restart your Claude Code session if it was already
running, and the next time you ask Claude to review a plan in this
project, it'll fan out to all three models in parallel and bring
back a consolidated report.

## Why this works without an install

Claude Code reads your project's `CLAUDE.md` on every session.
Any instruction you put there becomes part of how Claude behaves
in this project. The snippet above is just instructions: "when
reviewing a plan, also run these other CLIs and consolidate." No
binary, no plugin API, nothing to break when Claude Code updates.

If you'd rather have a one-shot script outside Claude Code, see
[`06-going-further/final/redteam.sh`](./06-going-further/final/redteam.sh)
— same method, ~100 lines of bash, takes a `plan.md` and writes a
ranked report.
