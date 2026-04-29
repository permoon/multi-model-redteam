#!/usr/bin/env bash
# 03b-consolidate.sh — Mini-lesson 3b: merge 3 raw outputs into one report.
#
# Demonstrates:
#   - Skip missing files (don't `cat` blindly when a team failed)
#   - Use Claude as the consolidator (you can swap any model via env var)
#   - Output schema enforcement via consolidation-prompt.md
#
# Run from this chapter directory after 03a-parallel.sh has succeeded:
#   bash 03b-consolidate.sh
set -euo pipefail

OUT_DIR=${1:-./out}
PROMPT_FILE=${2:-../prompts/consolidation-prompt.md}
CONSOL_CMD=${REDTEAM_CONSOLIDATOR:-"claude --print"}

[ -f "$PROMPT_FILE" ] || { echo "FAIL: $PROMPT_FILE not found"; exit 1; }

INPUT=""
COUNT=0
for t in claude codex gemini; do
  if [ -s "$OUT_DIR/$t.md" ]; then
    INPUT="$INPUT
=== Team $t ===
$(cat "$OUT_DIR/$t.md")"
    COUNT=$((COUNT+1))
  else
    echo "  skip team $t (no output)"
  fi
done

[ "$COUNT" -lt 2 ] && { echo "ERROR: need >= 2 teams, got $COUNT"; exit 1; }

PROMPT_TEMPLATE="$(cat "$PROMPT_FILE")"
echo "$PROMPT_TEMPLATE
$INPUT" | $CONSOL_CMD > "$OUT_DIR/consolidated.md"
echo "✓ Consolidated $COUNT teams → $OUT_DIR/consolidated.md"
