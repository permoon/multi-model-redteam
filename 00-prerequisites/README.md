# Chapter 00 — Prerequisites

## What you'll do in this chapter

- Install Claude Code, Codex CLI, Gemini CLI
- Get API keys for all three
- Estimate your budget (target: < $5 to complete the whole course)
- Verify your environment with `check-env.sh`

## Install the three CLIs

### Claude Code
See [official install guide](https://docs.claude.com/en/docs/claude-code).

```bash
npm install -g @anthropic-ai/claude-code
claude --version  # should print a version
```

### Codex CLI
See [official install guide](https://github.com/openai/codex-cli).

```bash
npm install -g @openai/codex
codex --version
```

> **Important**: this tutorial requires `codex-cli v0.125+`. The earlier
> `v0.121` shipped with `gpt-5.5` as default, which is no longer supported.

### Gemini CLI
See [official install guide](https://github.com/google-gemini/gemini-cli).

```bash
npm install -g @google/gemini-cli
gemini --version
```

## Set API keys

```bash
# In your ~/.bashrc or ~/.zshrc:
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="..."
```

If you use ChatGPT account auth for Codex CLI (not API key), see Codex docs
for the OAuth flow. **Note**: ChatGPT-account Codex cannot use the bare
`gpt-5` model; use the default ChatGPT-allowed model.

## macOS users: install GNU timeout

The repo's scripts use `timeout` to bound LLM call durations. macOS doesn't
ship GNU `timeout` by default:

```bash
brew install coreutils    # provides `gtimeout`
```

The scripts auto-detect `timeout` or `gtimeout`, so once installed you don't
need to do anything else.

## Verify your environment

```bash
bash check-env.sh
```

Expected output:
```
✓ Found timeout: /opt/homebrew/bin/gtimeout
Checking Claude Code...
Checking Codex CLI...
Checking Gemini CLI...
✓ All checks passed.
  Add to your shell rc to skip auto-detect on every run:
    export REDTEAM_TIMEOUT_CMD=/opt/homebrew/bin/gtimeout
```

If any check fails, it tells you which command and what to install.

## Budget estimate

Per full red-team run on a typical plan:

| Plan size | Tokens (3 models) | Cost (USD) |
|-----------|-------------------|------------|
| Small (sample-plan.md, ~50 lines) | ~5k in, ~5k out | ~$0.05 |
| Medium (chapter 4 BQ plan, ~100 lines) | ~10k in, ~12k out | ~$0.30 |
| Large (chapter 5 GCP plan, ~150 lines) | ~15k in, ~15k out | ~$0.50 |

Whole course (chapters 1–6 ~6 runs total): **< $5**.

## Common pitfalls

- **macOS without coreutils** → `timeout: command not found`. Fix with
  `brew install coreutils`.
- **Codex CLI v0.121 or older** → "model not supported". Upgrade to v0.125+.
- **ChatGPT account using `gpt-5` directly** → 400 error. Use default
  ChatGPT-allowed model.
- **Gemini CLI in some regions** → first call fails with "API not enabled".
  Enable the relevant API in your GCP console.
- **Windows native (no WSL)** → bash `&` / `wait` parallel syntax not
  supported reliably. Use WSL.

## Next

[Chapter 01 — Why one LLM isn't enough](../01-why-one-llm-isnt-enough/)
