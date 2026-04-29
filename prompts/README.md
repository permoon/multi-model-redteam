# Prompts

Three prompts that are the core IP of this tutorial. **Released under CC0** —
copy freely, no attribution required.

| File | Purpose |
|------|---------|
| [`system-prompt.md`](./system-prompt.md) | The 5-failure-dimension red team prompt. Use against any design plan. |
| [`consolidation-prompt.md`](./consolidation-prompt.md) | Merge 3 independent reviews into consensus + unique findings. |
| [`severity-prompt.md`](./severity-prompt.md) | Rank findings as must-fix / should-fix / accept. |

## Standalone usage (no install needed)

You don't need this whole repo. Just paste `system-prompt.md` + your plan
into any LLM chat UI:

- [Claude](https://claude.ai) or Claude Code
- [ChatGPT](https://chat.openai.com) or Codex CLI
- [Gemini](https://gemini.google.com) or Gemini CLI

For the full multi-LLM workflow (3 in parallel + consolidate + rank), see
the [course chapters](../README.md#course-outline).

## Why CC0

These prompts are the methodological core of this repo. Putting them under
CC0 means:
- No friction for adoption — anyone can use them in commercial work
- No attribution overhead — copy them into your internal tooling
- No license incompatibility — works with any downstream license

Code in the rest of this repo is MIT.

## Variants

Want to fork these prompts for your team's domain? Common adaptations:
- Add a 6th dimension (e.g., "compliance" for regulated industries)
- Replace `MUST-FIX / SHOULD-FIX / ACCEPT` with your team's severity scale
- Tighten / loosen the "≥2 concrete scenarios" rule

If you make a useful variant, an issue / PR with the use case is welcome
(but not required).
