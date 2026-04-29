#!/usr/bin/env bash
# redteam.sh — multi-LLM design red team CLI
#
# Usage:
#   ./redteam.sh <plan.md> [out_dir]
#
# Optional env vars:
#   REDTEAM_PROMPTS      prompt dir (default: ./prompts)
#   REDTEAM_TIMEOUT      per-call timeout in seconds (default: 180)
#   REDTEAM_TIMEOUT_CMD  path to GNU timeout (default: auto-detect)
#   REDTEAM_CLAUDE_CMD   default "claude --print"
#   REDTEAM_CODEX_CMD    default "codex exec --print"
#   REDTEAM_GEMINI_CMD   default "gemini --print"
set -euo pipefail

PLAN=${1:?usage: $0 <plan.md> [out_dir]}
OUT=${2:-./redteam-out-$(date +%Y%m%d-%H%M%S)}
PROMPT_DIR=${REDTEAM_PROMPTS:-./prompts}
TIMEOUT_SEC=${REDTEAM_TIMEOUT:-180}
TIMEOUT_CMD="${REDTEAM_TIMEOUT_CMD:-$(command -v timeout || command -v gtimeout || true)}"
CLAUDE_CMD=${REDTEAM_CLAUDE_CMD:-"claude --print"}
CODEX_CMD=${REDTEAM_CODEX_CMD:-"codex exec --print"}
GEMINI_CMD=${REDTEAM_GEMINI_CMD:-"gemini --print"}

[ -z "$TIMEOUT_CMD" ] && { echo "FAIL: install GNU timeout (macOS: brew install coreutils)"; exit 1; }
[ -f "$PROMPT_DIR/system-prompt.md" ] || { echo "FAIL: $PROMPT_DIR/system-prompt.md not found (override with REDTEAM_PROMPTS)"; exit 1; }
[ -f "$PLAN" ] || { echo "FAIL: plan file '$PLAN' not found"; exit 1; }

mkdir -p "$OUT"

PROMPT="$(cat "$PROMPT_DIR/system-prompt.md")
---
$(cat "$PLAN")
---"

# Bash arrays don't propagate from subshells, so we use status files instead.
run_team() {
  local name=$1 cli=$2
  local start=$SECONDS
  if echo "$PROMPT" | "$TIMEOUT_CMD" "$TIMEOUT_SEC" $cli > "$OUT/$name.md" 2>"$OUT/$name.err"; then
    echo "ok" > "$OUT/$name.status"
  else
    echo "fail" > "$OUT/$name.status"
  fi
  echo $((SECONDS-start)) > "$OUT/$name.duration"
  echo "  [$name] $(cat "$OUT/$name.status") ($(cat "$OUT/$name.duration")s, $(wc -l <"$OUT/$name.md" 2>/dev/null || echo 0) lines)"
}

echo "Running 3 teams in parallel (timeout=${TIMEOUT_SEC}s, cmd=$TIMEOUT_CMD)..."
run_team claude "$CLAUDE_CMD" &
run_team codex  "$CODEX_CMD"  &
run_team gemini "$GEMINI_CMD" &
wait

read_status()   { cat "$OUT/$1.status"   2>/dev/null || echo "unknown"; }
read_duration() { cat "$OUT/$1.duration" 2>/dev/null || echo "0"; }

cat > "$OUT/manifest.json" <<EOF
{
  "run_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "plan_file": "$PLAN",
  "timeout_cmd": "$TIMEOUT_CMD",
  "timeout_sec": $TIMEOUT_SEC,
  "teams": {
    "claude": {"status": "$(read_status claude)", "duration_s": $(read_duration claude)},
    "codex":  {"status": "$(read_status codex)",  "duration_s": $(read_duration codex)},
    "gemini": {"status": "$(read_status gemini)", "duration_s": $(read_duration gemini)}
  }
}
EOF

SUCCESS=0
for t in claude codex gemini; do
  [ "$(read_status "$t")" = "ok" ] && SUCCESS=$((SUCCESS+1))
done
[ $SUCCESS -lt 2 ] && { echo "ERROR: only $SUCCESS team(s) succeeded, need >= 2 (see $OUT/manifest.json)"; exit 1; }

echo "Consolidating ($SUCCESS teams)..."
INPUT=""
for t in claude codex gemini; do
  [ "$(read_status "$t")" = "ok" ] && INPUT="$INPUT
=== Team $t ===
$(cat "$OUT/$t.md")"
done

CONSOL_PROMPT="$(cat "$PROMPT_DIR/consolidation-prompt.md")
$INPUT"
echo "$CONSOL_PROMPT" | $CLAUDE_CMD > "$OUT/consolidated.md"

echo "Ranking severity..."
RANK_PROMPT="$(cat "$PROMPT_DIR/severity-prompt.md")
$(cat "$OUT/consolidated.md")"
echo "$RANK_PROMPT" | $CLAUDE_CMD > "$OUT/ranked.md"

echo
echo "Done. Outputs in $OUT/:"
echo "  {claude,codex,gemini}.md   (raw team outputs)"
echo "  manifest.json              (run metadata)"
echo "  consolidated.md            (merged findings)"
echo "  ranked.md                  (severity-ranked, FINAL)"
