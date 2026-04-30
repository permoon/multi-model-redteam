# Chapter 06 — Going further

> ### ⚠️ Read this first — three traps that bite when you extend
>
> 1. **Cost blowup.** A 500-line plan, three models, ~30k tokens
>    each = $0.50–2.00 per run. Iterate on a *summary* of the plan
>    first (compress to ~5k tokens), and only run the full plan when
>    your method has stabilised. Skip this and you'll burn $20
>    chasing a prompt tweak over an afternoon.
> 2. **Consensus failure (the echo chamber).** All three models are
>    transformers, all three learned from overlapping text on the
>    internet. So they share blind spots. Three-way agreement isn't
>    the same as truth — sometimes it just means three models all
>    missed the same thing. The fix isn't a fourth model. It's
>    keeping a regression list of human-found bugs in your
>    consolidation prompt, so the system learns from the misses you
>    catch by hand.
> 3. **Model bias bleeds into consolidation.** Claude over-warns;
>    Codex skips integration details; Gemini stays surface-level.
>    If your consolidation prompt itself runs on Claude (as ours
>    does in `final/redteam.sh`), you get Claude's bias on top of
>    Claude's findings. Worth noting in the report. Not always
>    worth solving.

## What's here

- [`final/redteam.sh`](./final/redteam.sh) — 100 lines (73 of code),
  with all features integrated: parallel run, manifest, 2-of-3
  fallback, consolidation, severity ranking
- This README — the pitfalls above and the extension ideas below

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

- **Add a 4th model with a different base architecture** — for
  example, Aider against an open model. This helps with the echo
  chamber, but only if the base architecture genuinely diverges.
  Adding a fourth GPT-family model adds little.
- **Wire it into your PR review bot** — gate merges on "no
  unaddressed must-fix findings." Caveat: false-positive rate on
  short PRs is high. Works much better at the design / RFC level
  than at line-level.
- **Multi-language plan support** — current prompts assume English
  markdown. For YAML-only or Terraform-only or SQL-only inputs, the
  consolidation step needs the file format hinted explicitly in the
  prompt.
- **Modular prompt templates** — split the system prompt by domain
  (data pipeline / web service / IAM-heavy / etc.) so the reviewers
  emphasise the failure modes that actually matter for the artifact
  in front of them.

## What's *not* here (intentionally)

- `pip install` packaging, GitHub Action, docker image, homebrew tap
- Custom CLI flags, profile system, plugin architecture
- A polished web UI

These all belong to a future Phase 2 CLI repo, separate from this
teaching repo. The point of this repo is the *method* — three
prompts, one shell script, two cases. If you find the method useful
and want a productised version, watch
[github.com/permoon](https://github.com/permoon) for the Phase 2
announcement, or open an issue saying you want it.

[← Back to README](../README.md) · [中文版](./README.zh-TW.md)
