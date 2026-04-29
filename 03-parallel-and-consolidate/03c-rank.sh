#!/usr/bin/env bash
# 03c-rank.sh — Mini-lesson 3c: assign severity to consolidated findings.
#
# Demonstrates:
#   - Severity rubric (must-fix / should-fix / accept) via prompt
#   - Hard caps to avoid noise (≤ 5 must-fix unless architectural)
#
# Run from this chapter directory after 03b-consolidate.sh:
#   bash 03c-rank.sh
set -euo pipefail

CONSOLIDATED=${1:-./out/consolidated.md}
PROMPT_FILE=${2:-../prompts/severity-prompt.md}
RANK_CMD=${REDTEAM_RANKER:-"claude --print"}

[ -s "$CONSOLIDATED" ] || { echo "ERROR: $CONSOLIDATED missing or empty"; exit 1; }
[ -f "$PROMPT_FILE" ] || { echo "FAIL: $PROMPT_FILE not found"; exit 1; }

PROMPT="$(cat "$PROMPT_FILE")
$(cat "$CONSOLIDATED")"

echo "$PROMPT" | $RANK_CMD > "${CONSOLIDATED%.md}-ranked.md"
echo "✓ Ranked → ${CONSOLIDATED%.md}-ranked.md"
