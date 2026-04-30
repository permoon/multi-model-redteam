#!/usr/bin/env bash
# compare-models.sh — run two LLMs sequentially on the same code, save both outputs.
#
# Goal: see which findings each model surfaces, and which they miss. Diff them
# manually after — that's chapter 01's whole point.
set -euo pipefail

cd "$(dirname "$0")"

TARGET=${1:-target-code.py}
[ -f "$TARGET" ] || { echo "FAIL: $TARGET not found"; exit 1; }

PROMPT="Review this code. List bugs and design issues you'd flag in a PR.
Be concrete: name the line, the failure mode, and how to fix.

$(cat "$TARGET")"

echo "[1/2] Running Claude..."
echo "$PROMPT" | claude --print > review-claude.md

echo "[2/2] Running Codex..."
echo "$PROMPT" | codex exec --skip-git-repo-check > review-codex.md

echo
echo "Done. Compare manually:"
echo "  - review-claude.md"
echo "  - review-codex.md"
echo
echo "Or:  diff review-claude.md review-codex.md"
echo "     (most diffs will be wording, not findings — read both in full)"
