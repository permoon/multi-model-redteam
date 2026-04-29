---
case: "<case name, e.g. bq-pipeline | gcp-deploy | sample-plan>"
run_at: "<UTC ISO timestamp, e.g. 2026-05-01T08:30:00Z>"
plan_file: "<relative path to plan.md, e.g. examples/sample-plan.md>"
models:
  claude:
    cli_version: "<output of `claude --version`>"
    model: "<as configured in your env>"
    flags: "--print"
  codex:
    cli_version: "<output of `codex --version`>"
    model: "<as configured>"
    flags: "exec --print"
  gemini:
    cli_version: "<output of `gemini --version`>"
    model: "<as configured>"
    flags: "--print"
timeout_sec: 180
notes: |
  Output is non-deterministic. Findings below are from THIS specific run;
  your output may differ in wording but should match the pattern.
---

# Expected findings

> Replace the metadata header above with your actual run values, then list
> the consolidated findings below.

## Consensus Findings (≥ 2 teams)

| # | Finding | Teams | Severity |
|---|---------|-------|----------|
| 1 | ... | Claude, Codex | must-fix |

## Unique Findings

| # | Finding | Team | Severity |
|---|---------|------|----------|
| 2 | ... | Gemini | should-fix |

## Apparent Disagreements

- Claude says X; Codex says Y. Both valid; team chooses.

## Coverage Gaps

- Dimension N had < 2 concrete scenarios across all teams.

## Triple Blind Spot (humans found, all 3 LLMs missed)

- ...
