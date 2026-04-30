# Chapter 00 — Prerequisites

A few things to install before chapter 1. Should take about 10 minutes
if you've never used these CLIs before, less if you have.

## What you'll do here

- Install Claude Code, Codex CLI, and Gemini CLI
- Get API keys for all three
- Check your budget (the goal: stay under $5 for the whole course)
- Run `check-env.sh` to confirm everything works

## Install the three CLIs

### Claude Code

[Official install guide](https://docs.claude.com/en/docs/claude-code).

```bash
npm install -g @anthropic-ai/claude-code
claude --version  # should print a version
```

### Codex CLI

[Official install guide](https://github.com/openai/codex-cli).

```bash
npm install -g @openai/codex
codex --version
```

> **Important**: this tutorial requires `codex-cli v0.125+`. Earlier
> `v0.121` shipped with `gpt-5.5` as the default, which is no longer
> supported. Upgrade if you have an older version.

### Gemini CLI

[Official install guide](https://github.com/google-gemini/gemini-cli).

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

If you use ChatGPT account auth for Codex CLI instead of an API key,
follow Codex's docs for the OAuth flow. **Note**: ChatGPT-account
Codex can't use the bare `gpt-5` model, so use the default
ChatGPT-allowed model.

## macOS users: install GNU timeout

The scripts in this repo use `timeout` to bound how long any one LLM
call can run. macOS doesn't ship GNU `timeout` by default:

```bash
brew install coreutils    # this gives you `gtimeout`
```

The scripts auto-detect either `timeout` or `gtimeout`, so once
you've installed it you don't need to do anything else.

## Check your environment

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

If anything fails, the script tells you which command and what to
install.

## Budget

Per full red-team run on a typical plan:

| Plan size | Tokens (3 models) | Cost (USD) |
|-----------|-------------------|------------|
| Small (sample-plan.md, ~50 lines) | ~5k in, ~5k out | ~$0.05 |
| Medium (chapter 4 BQ plan, ~100 lines) | ~10k in, ~12k out | ~$0.30 |
| Large (chapter 5 GCP plan, ~150 lines) | ~15k in, ~15k out | ~$0.50 |

The whole course (chapters 1–6, about 6 runs total): **under $5**.

## Things that go wrong

A short list of things readers have actually hit:

- **macOS without coreutils.** Error: `timeout: command not found`.
  Fix: `brew install coreutils`.
- **Codex CLI v0.121 or older.** Error mentioning "model not
  supported". Fix: upgrade to v0.125+.
- **ChatGPT account using `gpt-5` directly.** Returns a 400. Use the
  default ChatGPT-allowed model instead.
- **Gemini CLI in some regions.** First call fails with "API not
  enabled". Fix: enable the relevant API in your GCP console.
- **Windows native (no WSL).** Bash `&` and `wait` parallel syntax
  isn't reliable there. Use WSL.

## Next

[Chapter 01 — Why one LLM isn't enough](../01-why-one-llm-isnt-enough/)

[← Back to README](../README.md) · [中文版](./README.zh-TW.md)
