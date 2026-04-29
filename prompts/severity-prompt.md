Take this consolidated red-team report and assign severity to every finding.

Categories:
- MUST-FIX: data loss, security vuln, irreversible op, direct SLO violation
- SHOULD-FIX: edge cases, perf issues, maintainability concerns
- ACCEPT: known limitation, low probability + low impact, has monitoring as
  compensating control

Output format (markdown table):

| # | Finding (one-line) | Category | Reasoning | Estimated effort |

Rules:
- If unsure between MUST and SHOULD, choose MUST. Bias toward conservative.
- "Estimated effort" must be one of: <1hr, half-day, multi-day. Reject
  vague effort estimates.
- Reject ACCEPT for anything touching auth, billing, or PII.
- Cap MUST-FIX at 5 entries unless the design is clearly broken at the
  architecture level. If you exceed 5, the prompt or design is too
  ambitious for one review pass.

Consolidated report:
{CONSOLIDATED}
