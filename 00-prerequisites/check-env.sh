#!/usr/bin/env bash
# check-env.sh — verify three CLIs, API keys, and platform deps
set -euo pipefail

# 1. timeout / gtimeout (macOS lacks GNU timeout by default)
TIMEOUT_CMD="$(command -v timeout || command -v gtimeout || true)"
if [ -z "$TIMEOUT_CMD" ]; then
  echo "FAIL: GNU timeout not found."
  echo "  macOS: brew install coreutils    # gives you gtimeout"
  echo "  Linux: apt install coreutils     # or your distro equivalent"
  exit 1
fi
echo "✓ Found timeout: $TIMEOUT_CMD"

# 2. Three CLIs and their APIs
echo "Checking Claude Code..."
claude --version >/dev/null 2>&1 || { echo "FAIL: claude CLI not found"; exit 1; }
echo "say only the word 'ok'" | claude --print | grep -qi ok \
  || { echo "FAIL: claude API call did not return 'ok' (auth or quota?)"; exit 1; }

echo "Checking Codex CLI..."
codex --version >/dev/null 2>&1 || { echo "FAIL: codex CLI not found"; exit 1; }
echo "say only the word 'ok'" | codex exec --print | grep -qi ok \
  || { echo "FAIL: codex API call did not return 'ok'"; exit 1; }

echo "Checking Gemini CLI..."
gemini --version >/dev/null 2>&1 || { echo "FAIL: gemini CLI not found"; exit 1; }
echo "say only the word 'ok'" | gemini --print | grep -qi ok \
  || { echo "FAIL: gemini API call did not return 'ok'"; exit 1; }

# 3. jq, curl
command -v jq   >/dev/null || { echo "FAIL: jq missing"; exit 1; }
command -v curl >/dev/null || { echo "FAIL: curl missing"; exit 1; }

echo
echo "✓ All checks passed."
echo "  Add to your shell rc to skip auto-detect on every run:"
echo "    export REDTEAM_TIMEOUT_CMD=$TIMEOUT_CMD"
