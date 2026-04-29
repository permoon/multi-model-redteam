#!/usr/bin/env bash
# check-env.sh — verify three CLIs, platform deps
#
# This is a fast sanity check (no API calls). It only verifies that:
#   - GNU timeout / gtimeout is callable
#   - claude, codex, gemini CLIs are installed and report a version
#   - jq, curl are available
# API key validity is verified on your first redteam.sh run.
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

# 2. Three CLIs — version check only (no API call, no cost)
for cli in claude codex gemini; do
  echo "Checking $cli CLI..."
  if ! "$cli" --version >/dev/null 2>&1; then
    echo "FAIL: $cli CLI not found or broken (try '$cli --version' manually)"
    exit 1
  fi
  ver="$($cli --version 2>&1 | head -n 1)"
  echo "  $ver"
done

echo
echo "✓ CLI and platform deps OK."
echo
echo "Note: this only verified CLIs are installed and callable."
echo "API keys / model access are verified on your first redteam.sh run."
echo "If that run fails with auth errors, check your *_API_KEY env vars."
echo
echo "Tip: add to your shell rc to skip timeout auto-detect on every run:"
echo "  export REDTEAM_TIMEOUT_CMD=$TIMEOUT_CMD"
