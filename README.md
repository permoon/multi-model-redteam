# multi-model-redteam

> A 100-line bash that runs 3 LLMs as your design red team. Find what one model misses.

> **Not jailbreak red teaming.** This is design review red teaming for
> AI-assisted software planning. If you're looking for prompt injection /
> safety alignment, see [garak](https://github.com/leondz/garak) or
> [promptfoo](https://github.com/promptfoo/promptfoo).

[中文 README](./README.zh-TW.md) · [Methodology](./docs/methodology.md) · [Course outline](#course-outline)

![demo](./assets/hero.gif)

## Quick start (5 lines)

```bash
git clone https://github.com/permoon/multi-model-redteam.git
cd multi-model-redteam
export ANTHROPIC_API_KEY=... OPENAI_API_KEY=... GEMINI_API_KEY=...
bash 06-going-further/final/redteam.sh examples/sample-plan.md
# → ./redteam-out-<timestamp>/ranked.md
```

Cost: ~$0.05 for the sample plan, ~$0.50–2.00 for production-size plans.

## Don't want to install? Copy this prompt directly

You can paste this into Claude / ChatGPT / Gemini chat UI without any setup:

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

The full method (3 LLMs in parallel + consolidation + severity ranking) is
in the [Course outline](#course-outline) below.

## What you get from one run

Example output (Day 4 actual run on the BigQuery pipeline case — see
[chapter 4](./04-case-bq-pipeline/) for the full plan + raw outputs):

<details>
<summary>📋 Example findings (truncated)</summary>

> **Note**: this is filled in on Day 4 of the build (real output from running
> all three models against `04-case-bq-pipeline/plan.md`). Currently empty
> because the case has not been run yet.

</details>

## Why this exists

You already use Claude Code (or Cursor, or Codex CLI) to review your designs.
It catches a lot. But every model has blind spots:

- **Claude** over-engineers defensiveness
- **Codex** skips integration details
- **Gemini** stays surface-level

Run **three** in parallel against the same plan, with the same prompt, no
cross-talk. Then consolidate. The findings only one model caught are gold.

## What you'll build

By the end of 7 chapters:
- A `redteam.sh` (< 100 lines) that takes any `plan.md` and produces a
  severity-ranked findings report from 3 LLMs in parallel
- Reusable prompts for the 5-failure-dimension frame
- Two real-world cases: BigQuery pipeline + GCP Cloud Run deploy

## Prerequisites

- **Bash 4+** (works on Git Bash on Windows; macOS bash 3.2 also OK)
- **GNU `timeout`** (macOS users: `brew install coreutils` gives you
  `gtimeout`; scripts auto-detect)
- Three LLM CLIs installed and authenticated:
  - [Claude Code](https://docs.claude.com/en/docs/claude-code)
  - [Codex CLI](https://github.com/openai/codex-cli)
  - [Gemini CLI](https://github.com/google-gemini/gemini-cli)
- API keys for all three (free tiers cover chapters 1–3; chapters 4–5 need
  ~$5 total)

> **Tested with**: claude-code vX.Y, codex-cli v0.125+, gemini-cli vX.Y
> (as of 2026-04). The three CLIs are not stable public APIs — flags / auth
> / default model may change. If your version differs, see
> [00-prerequisites](./00-prerequisites/).

See [00-prerequisites](./00-prerequisites/) for full setup.

## Course outline

| # | Chapter | What you'll learn |
|---|---------|-------------------|
| 00 | [Prerequisites](./00-prerequisites/) | Install 3 CLIs, get API keys, budget |
| 01 | [Why one LLM isn't enough](./01-why-one-llm-isnt-enough/) | Single vs second model: divergence in action |
| 02 | [The 5-prompt frame](./02-the-five-frame/) | The methodology core |
| 03 | [Parallel + consolidate + rank](./03-parallel-and-consolidate/) | Bash `&` + 4th LLM call + severity |
| 04 | [Case: BQ pipeline](./04-case-bq-pipeline/) | Real BigQuery design with 7 hidden flaws |
| 05 | [Case: GCP deploy](./05-case-gcp-deploy/) | Cloud Run + Workflows, IAM/region traps |
| 06 | [Going further](./06-going-further/) | Final 100-line `redteam.sh` + extension ideas |

## What this is NOT

- **Not jailbreak / safety-alignment red teaming.** That's a different
  field.
- **Not a polished CLI.** Phase 2 will be a separate repo with `pip
  install`, GitHub Actions, etc. This repo is a tutorial.
- **Not an orchestrator framework.** The world doesn't need another one.

## Standalone prompts

The three prompts in [`prompts/`](./prompts/) are released under **CC0**.
Use them anywhere — chat UI, your own pipeline, internal tooling.
Attribution appreciated, not required.

## License

Code & docs: MIT. Prompts in [`prompts/`](./prompts/): CC0.

## Acknowledgements

Heavily inspired by:
- [karpathy/micrograd](https://github.com/karpathy/micrograd) — minimal
  teaching repo done right
- [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch) —
  chapter-folder pedagogy

— Hector ([@permoon](https://github.com/permoon))
