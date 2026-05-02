# multi-model-redteam

> Three LLMs review your design in parallel. Whatever one misses, the other two often catch.
>
> **No install. No plugin. No marketplace. No npm or pip.** Paste ~30 lines into your `CLAUDE.md` and the next time Claude Code reviews a plan, it fans out to Codex CLI and Gemini CLI in parallel and consolidates the findings.

> **Not jailbreak red teaming.** AI is doing more than just writing
> code now — it's drafting the plans that drive the code. Any flaw
> that slips into the plan ripples through everything AI builds from
> it. Catching design issues at the plan stage, before code gets
> written, matters more than it used to. That's what this repo is
> for.

> If you're looking for prompt injection or safety alignment, see
> [garak](https://github.com/leondz/garak) or
> [promptfoo](https://github.com/promptfoo/promptfoo).

[中文 README](./README.zh-TW.md) · [Methodology](./docs/methodology.md) · [Course outline](#course-outline) · [Write-up on DEV ↗](https://dev.to/hector_haung_da45eb10a814/ai-is-very-good-at-implementing-bad-plans-4d80)

![multi-model-redteam — one model misses, the other two often catch](./assets/hero.png)

> 📖 **Full write-up on DEV**: [AI Is Very Good at Implementing Bad Plans](https://dev.to/hector_haung_da45eb10a814/ai-is-very-good-at-implementing-bad-plans-4d80) — the story behind this repo, the alias-shadowing bug only Claude caught, and why 3 models break the echo chamber.

## Three ways to run it. None require an install of this repo.

Pick the tier that fits. Each is self-contained.

### Tier 0 — Paste ~30 lines into your `CLAUDE.md`

If you're already using Claude Code and have Codex CLI + Gemini
CLI on your `PATH` (chapter 0 walks you through those), this is
the lowest-friction path. **That's the install:**

1. Open your project's `CLAUDE.md` (the file Claude Code reads on
   every session)
2. Append the snippet from
   [`claude-md-snippet.md`](./claude-md-snippet.md)
3. That's it. **No plugin, no marketplace, no npm, no pip,
   nothing to install for this repo.**

The next time you ask Claude Code to review a plan in this
project, it fans out to Codex CLI and Gemini CLI in parallel and
brings back a consolidated report.

### Tier 1 — Run the bash script

Want to red-team a `plan.md` outside Claude Code? Five-line
setup:

```bash
git clone https://github.com/permoon/multi-model-redteam.git
cd multi-model-redteam
export ANTHROPIC_API_KEY=... OPENAI_API_KEY=... GEMINI_API_KEY=...
bash 06-going-further/final/redteam.sh examples/sample-plan.md
# → ./redteam-out-<timestamp>/ranked.md
```

Cost: about $0.10–0.20 for the sample plan, $0.50–2.00 for
production-size plans. Wall time ~5–15 minutes (the consolidate +
rank steps dominate).

### Tier 2 — Paste the prompt into a chat UI

No CLI installed at all? Copy the prompt below into Claude,
ChatGPT, or Gemini's chat UI. You'll only get one model's review
this way, but it's still a lot better than reviewing without a
frame.

<details>
<summary>📋 The 5-failure-dimension red team prompt</summary>

```
You are the red team for this design.

Cover all 5 dimensions below. For each, provide AT LEAST 2 concrete failure
scenarios (not abstract descriptions):

1. HIDDEN ASSUMPTIONS — ordering, uniqueness, atomicity, data freshness,
   caller behavior. What does this design implicitly depend on?
2. DEPENDENCY FAILURES — upstream/downstream services, external APIs,
   databases, messaging. What breaks if any dependency degrades?
3. BOUNDARY INPUTS — empty, single, huge batch, malicious, malformed.
   What happens at p99 and at malicious-percentile inputs?
4. MISUSE PATHS — caller misbehavior, user skipping steps, out-of-order
   operations. What if humans don't follow the plan?
5. ROLLBACK & BLAST RADIUS — how to recover, scope of damage. 5-minute
   detection vs 5-day detection?

For each scenario, include:
- TRIGGER: what causes it
- IMPACT: who is affected, how badly
- DETECTABILITY: how long until noticed

Be concrete. Reject abstract advice like "add monitoring". Specify what
metric, what threshold, what alert.

Design to review:
---
{PASTE PLAN HERE}
---
```

</details>

The full method (3 LLMs in parallel + consolidation + severity
ranking) is in the [course outline](#course-outline) below.

## What you get from one run

Example output from a real run on the BigQuery pipeline case
(see [chapter 4](./04-case-bq-pipeline/) for the full plan and the
curated canonical findings):

<details>
<summary>📋 Example findings (chapter 04, 2026-04-29 canonical run, abbreviated)</summary>

**All 3 models flagged this:**

- `INSERT INTO order_events_dedup` is not idempotent. Any retry
  doubles yesterday's rows. The existing "less-than-50%-of-expected"
  alert is one-sided and can't catch over-counts.

**Only Claude found this:**

- **Step D's correlated subquery has unqualified column references,
  so the imputation step silently does nothing after day one.** Codex
  and Gemini both *cited* this same SQL block in their reviews and
  carried on assuming it worked. Neither tested whether `WHERE
  m2.user_id = user_id` actually binds the way the writer intended in
  BigQuery's scoping rules. The project's whole purpose (filling in
  missing checkout events) would silently fail for 2–8 weeks before
  anyone noticed.

**Only Gemini found this:**

- **Midnight-boundary race in dedup across partitions.** The same
  event retried at 23:59:59 on Day 1 and 00:00:02 on Day 2 lands in
  different daily partitions. Step C's `GROUP BY` only sees within a
  day, so the cross-partition pair never gets deduped.

**Only Codex found this:**

- **Truncated CSV from GCS, BQ load succeeds anyway.** Up to ~50% of
  the data can be silently lost and still pass the row-count alert,
  because the truncated file is still syntactically valid. You can
  only catch this by reconciling row counts across Postgres, GCS,
  and BigQuery.

Full output: [04-case-bq-pipeline/expected-findings.md](./04-case-bq-pipeline/expected-findings.md)
(13 consensus + 11 unique + 3 triple-blind-spot findings).

</details>

## Why this exists

You're already using Claude Code (or Cursor, or Codex CLI) to look
over your designs. It works. But each model has its own quirks:

- **Claude** tends to over-warn — flagging extra defensive checks
  that aren't really bugs
- **Codex** is more concise and sometimes skips integration details
- **Gemini** stays surface-level and doesn't always dig into
  specifics

Have all three review the same plan, with the same prompt, without
seeing each other's outputs. Then merge their findings. The bugs
that only one model caught — that's where the value is. Those are
the ones a single-model review would have quietly missed.

## What you'll build

By the end of seven chapters you'll have:

- A 100-line `redteam.sh` that takes any `plan.md` and gives back a
  severity-ranked findings report from 3 LLMs running in parallel
- Reusable prompts for the 5-failure-dimension frame
- Two real cases worked out in detail: a BigQuery pipeline and a
  GCP Cloud Run deploy

## Prerequisites

- **Bash 3.2+** (tested on macOS bash 3.2, Linux bash 5, and Git Bash on Windows)
- **GNU `timeout`** (macOS users: `brew install coreutils` gives you
  `gtimeout`; the scripts auto-detect it)
- The three LLM CLIs installed and authenticated:
  - [Claude Code](https://docs.claude.com/en/docs/claude-code)
  - [Codex CLI](https://github.com/openai/codex-cli)
  - [Gemini CLI](https://github.com/google-gemini/gemini-cli)
- API keys for all three (free tiers cover chapters 1–3; chapters
  4–5 need ~$5 total)

> **Tested with**: claude-code v2.1.114, codex-cli v0.125.0,
> gemini-cli v0.36.0 (as of 2026-04). The three CLIs aren't stable
> public APIs — flags, auth, and default models can change. If your
> version differs, see [00-prerequisites](./00-prerequisites/).

See [00-prerequisites](./00-prerequisites/) for the full setup.

## Course outline

| # | Chapter | What you'll learn |
|---|---------|-------------------|
| 00 | [Prerequisites](./00-prerequisites/) | Install 3 CLIs, get API keys, budget |
| 01 | [Why one LLM isn't enough](./01-why-one-llm-isnt-enough/) | Single vs second model: divergence in action |
| 02 | [The 5-prompt frame](./02-the-five-frame/) | The methodology core |
| 03 | [Parallel + consolidate + rank](./03-parallel-and-consolidate/) | Bash `&` + a 4th LLM call + severity |
| 04 | [Case: BQ pipeline](./04-case-bq-pipeline/) | Real BigQuery design with 7 hidden flaws |
| 05 | [Case: GCP deploy](./05-case-gcp-deploy/) | Cloud Run + Workflows, IAM/region traps |
| 06 | [Going further](./06-going-further/) | Final 100-line `redteam.sh` + extension ideas |

## What this is NOT

- **Not jailbreak / safety-alignment red teaming.** Different field.
  See [garak](https://github.com/leondz/garak) or
  [promptfoo](https://github.com/promptfoo/promptfoo).
- **Not a polished CLI.** Phase 2 will be a separate repo with
  `pip install`, GitHub Actions, and so on. This repo is a tutorial.
- **Not yet another multi-agent orchestrator.** If you want an
  installed framework with marketplace plugins or consensus-gating
  CLIs, see [claude-octopus](https://github.com/nyldn/claude-octopus),
  [cerberus](https://github.com/charlieyou/cerberus), or
  [agent-council](https://github.com/yogirk/agent-council). This
  repo is the opposite shape: a tutorial plus ~30 lines of paste
  for your `CLAUDE.md`.

## Standalone prompts

The three prompts in [`prompts/`](./prompts/) are released under
**CC0**. Use them anywhere — chat UI, your own pipeline, internal
tooling. Attribution is appreciated but not required.

## License

Code & docs: MIT. Prompts in [`prompts/`](./prompts/): CC0.

## Acknowledgements

Heavy inspiration from:
- [karpathy/micrograd](https://github.com/karpathy/micrograd) — what
  a minimal teaching repo looks like done right
- [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch) —
  the chapter-folder pedagogy

— Hector ([@permoon](https://github.com/permoon))
