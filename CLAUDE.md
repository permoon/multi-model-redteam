# Project context for Claude Code

This file gives AI agents (Claude Code, Cursor, Aider, etc.) the minimum
context to navigate this repo.

## What this is

A teaching repo for **multi-LLM design red teaming**: run Claude Code,
Codex CLI, and Gemini CLI in parallel against a design plan, consolidate
findings, rank by severity. 7 chapters + 2 real-world cases, < 100 lines
of bash.

## What this is NOT

- Not jailbreak / safety-alignment red teaming
- Not a polished CLI (a separate `phase 2` repo will productize this)
- Not an orchestrator framework

## How the repo is organized

- `prompts/` — the three core prompts (CC0, copy freely)
- `00-prerequisites/` — install / API key / env check
- `01-why-one-llm-isnt-enough/` to `06-going-further/` — chapters in order
- `examples/sample-plan.md` — minimal plan for the quick-start
- `06-going-further/final/redteam.sh` — the 100-line CLI (the "hero
  artifact")

## Style

- Code: bash + minimal Python. No frameworks.
- Comments in English. Documentation prefers English first; Chinese
  versions are abridged in `README.zh-TW.md` style.
- Scripts must be cross-platform (macOS bash 3, Linux bash 5, WSL on
  Windows).
- All `timeout` calls auto-detect `timeout` vs `gtimeout`.

## Editing rules

- Do NOT add `# bug:` or `# 漏洞:` comments to `plan.md` files. Findings
  belong in `expected-findings.md`. (Background: case study fidelity
  requires that the plan be reviewed without spoilers.)
- Bash array state cannot cross subshell boundaries; use status files
  (`$OUT/$name.status`) for parallel jobs, not `declare -A`.
- Keep `final/redteam.sh` under 100 lines. If a feature requires more,
  it belongs in the future `phase 2` CLI repo, not here.

## Phase 2

A polished CLI (pip install, GitHub Action, docker image) is planned as
a separate repo. Do not add CLI polish here.
