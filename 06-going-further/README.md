# Chapter 06 — Going further

> ### ⚠️ Read this first — three traps that bite when you extend
>
> 1. **Cost blowup.** A 500-line plan × 3 models × ~30k tokens each
>    = $0.50–2.00 per run. Iterate on a *summary* of the plan first
>    (compress to ~5k tokens), then run the full plan only when the
>    method has stabilized. Otherwise you'll burn $20 chasing a prompt
>    tweak.
> 2. **Consensus failure (echo chamber).** All three models are
>    transformers trained on overlapping public corpora — they share
>    blind spots. Three-way agreement is *not* the same as truth. The
>    fix isn't a fourth model; it's keeping a regression list of
>    human-found bugs in your consolidation prompt so the system
>    learns from past misses.
> 3. **Model bias bleeds into consolidation.** Claude over-flags
>    defensiveness; Codex skips integration details; Gemini stays
>    surface-level. If your consolidation prompt itself runs on Claude
>    (as ours does in `final/redteam.sh`), you get Claude's bias on
>    top of Claude's findings. Worth noting in the report; not always
>    worth solving.

## What's here

- [`final/redteam.sh`](./final/redteam.sh) — 100 lines (73 lines of
  code), all features integrated: parallel run + manifest + 2-of-3
  fallback + consolidation + severity ranking
- This README — pitfalls (above) + extension ideas (below)

The script:

```bash
bash 06-going-further/final/redteam.sh examples/sample-plan.md
# → ./redteam-out-<timestamp>/
#     ├── claude.md, codex.md, gemini.md     (raw outputs)
#     ├── manifest.json                       (status + duration)
#     ├── consolidated.md                     (consensus + unique)
#     └── ranked.md                           (severity-ranked, FINAL)
```

Defaults are overridable via env vars — see the comment block at the
top of the script.

## Extension ideas

If you want to push this further, in roughly increasing effort:

- **Add a 4th model with a different base architecture** — e.g.,
  Aider against an open model. Helps with echo chamber, but only
  if the base architecture genuinely diverges (a fourth GPT-family
  model adds little).
- **Wire it to your PR review bot** — gate merges on "no
  unaddressed must-fix findings." Caveat: false-positive rate on
  short PRs is high; works better at design / RFC level than line-level.
- **Multi-language plan support** — current prompts assume English /
  markdown plans. For YAML / Terraform / SQL-only inputs, the
  consolidation step needs the file format hinted in the prompt.
- **Modular prompt templates** — split the system prompt by domain
  (data pipeline / web service / IAM-heavy / etc.) so reviewers
  emphasise the failure modes that matter for the artifact at hand.

## What's *not* here (intentionally)

- `pip install` packaging, GitHub Action, docker image, homebrew tap
- Custom CLI flags, profile system, plugin architecture
- A polished web UI

These all belong to a Phase 2 CLI repo (separate from this teaching
repo). The point of this repo is the *method* — three prompts, one
shell script, two cases. If you find the method useful and want it
operationalised, watch for the Phase 2 announcement on
[github.com/permoon](https://github.com/permoon) or open an issue
asking for it.

[← Back to README](../README.md) · [中文版](./README.zh-TW.md)
