#!/usr/bin/env bash
# 03a-parallel.sh — Mini-lesson 3a: launch 3 LLMs in parallel.
#
# A deliberately stand-alone, lesson-sized version of the parallel section
# of final/redteam.sh. Demonstrates:
#   - bash & + wait for true parallelism
#   - per-team status files (avoiding bash array scoping pitfalls)
#   - cross-platform timeout detection
#   - "≥ 2 teams must succeed" graceful degradation
#
# Run from this chapter directory:
#   bash 03a-parallel.sh ../examples/sample-plan.md
set -euo pipefail

# Run from this script's directory so default relative paths resolve.
cd "$(dirname "$0")"

PLAN_FILE=${1:?usage: $0 <plan.md>}
PROMPT_FILE=${2:-../prompts/system-prompt.md}
OUT_DIR=${3:-./out}
TIMEOUT_SEC=${REDTEAM_TIMEOUT:-180}
TIMEOUT_CMD="${REDTEAM_TIMEOUT_CMD:-$(command -v timeout || command -v gtimeout || true)}"
CLAUDE_CMD=${REDTEAM_CLAUDE_CMD:-"claude --print"}
CODEX_CMD=${REDTEAM_CODEX_CMD:-"codex exec --skip-git-repo-check"}
GEMINI_CMD=${REDTEAM_GEMINI_CMD:-"gemini"}

[ -z "$TIMEOUT_CMD" ] && { echo "FAIL: install GNU timeout (macOS: brew install coreutils)"; exit 1; }
[ -f "$PROMPT_FILE" ] || { echo "FAIL: $PROMPT_FILE not found (override with REDTEAM_PROMPTS)"; exit 1; }
[ -f "$PLAN_FILE" ] || { echo "FAIL: plan file '$PLAN_FILE' not found"; exit 1; }

mkdir -p "$OUT_DIR"
rm -f "$OUT_DIR"/{claude,codex,gemini}.{status,duration}

PROMPT="$(cat "$PROMPT_FILE")
---
$(cat "$PLAN_FILE")
---"

# Subprocesses cannot update parent shell's bash arrays, so we use status files.
# This was a real bug discovered in plan v3 review — see chapter README.
run_team() {
  local name=$1 cli=$2
  local start=$SECONDS
  if echo "$PROMPT" | "$TIMEOUT_CMD" "$TIMEOUT_SEC" $cli > "$OUT_DIR/$name.md" 2>"$OUT_DIR/$name.err"; then
    echo "ok" > "$OUT_DIR/$name.status"
  else
    echo "fail" > "$OUT_DIR/$name.status"
  fi
  echo $((SECONDS-start)) > "$OUT_DIR/$name.duration"
  echo "  [$name] $(cat "$OUT_DIR/$name.status") ($(cat "$OUT_DIR/$name.duration")s)"
}

echo "Running 3 teams in parallel (timeout=${TIMEOUT_SEC}s)..."
run_team claude "$CLAUDE_CMD" &
run_team codex  "$CODEX_CMD"  &
run_team gemini "$GEMINI_CMD" &
wait

read_status() { cat "$OUT_DIR/$1.status" 2>/dev/null || echo "unknown"; }

cat > "$OUT_DIR/manifest.json" <<EOF
{
  "run_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "plan_file": "$PLAN_FILE",
  "teams": {
    "claude": {"status": "$(read_status claude)"},
    "codex":  {"status": "$(read_status codex)"},
    "gemini": {"status": "$(read_status gemini)"}
  }
}
EOF

SUCCESS=0
for t in claude codex gemini; do
  [ "$(read_status "$t")" = "ok" ] && SUCCESS=$((SUCCESS+1))
done
[ "$SUCCESS" -lt 2 ] && { echo "ERROR: only $SUCCESS team(s) succeeded, need >= 2"; exit 1; }
echo "✓ $SUCCESS/3 teams succeeded. Outputs in $OUT_DIR/"
