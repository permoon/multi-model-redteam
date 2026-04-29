#!/usr/bin/env bash
# run-redteam.sh — run the multi-model red team on this case's plan.md.
#
# Outputs a timestamped directory with raw team outputs, manifest,
# consolidated findings, and severity ranking. Pick the canonical run,
# copy its consolidated.md to expected-findings.md, and prepend the
# metadata header from ../examples/expected-findings-template.md.
set -euo pipefail

# Always run from this script's directory so relative paths resolve correctly,
# regardless of where the user invokes the script from.
cd "$(dirname "$0")"

OUT="./out-$(date +%Y%m%d-%H%M%S)"
SCRIPT="../06-going-further/final/redteam.sh"

[ -f "$SCRIPT" ] || { echo "FAIL: $SCRIPT not found"; exit 1; }
[ -f "./plan.md" ] || { echo "FAIL: ./plan.md not found"; exit 1; }

REDTEAM_PROMPTS="../prompts" bash "$SCRIPT" ./plan.md "$OUT"

echo
echo "Done. Inspect:"
echo "  $OUT/ranked.md           — severity-ranked findings (FINAL)"
echo "  $OUT/consolidated.md     — merged consensus + unique findings"
echo "  $OUT/{claude,codex,gemini}.md  — raw team outputs"
echo
echo "When you've decided this is the canonical run for the chapter:"
echo "  1. cp $OUT/consolidated.md expected-findings.md"
echo "  2. Prepend the metadata header from ../examples/expected-findings-template.md"
echo "  3. git add expected-findings.md && git commit -m 'docs: chapter 05 expected findings (run \$DATE)'"
