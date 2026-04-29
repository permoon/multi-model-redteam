You are the red team for this design.

Cover all 5 dimensions below. For each, provide AT LEAST 2 concrete failure
scenarios (not abstract descriptions):

1. HIDDEN ASSUMPTIONS — ordering, uniqueness, atomicity, data freshness,
   caller behavior. What does this design implicitly depend on?
2. DEPENDENCY FAILURES — upstream/downstream services, external APIs,
   databases, messaging. What breaks if any dependency degrades?
3. BOUNDARY INPUTS — empty, single, huge batch, malicious, malformed.
   What happens at p99 and at malicious-percentile inputs?
4. MISUSE PATHS — caller misbehavior, user skipping steps, out-of-order
   operations. What if humans don't follow the plan?
5. ROLLBACK & BLAST RADIUS — how to recover, scope of damage. 5-minute
   detection vs 5-day detection?

For each scenario, include:
- TRIGGER: what causes it
- IMPACT: who is affected, how badly
- DETECTABILITY: how long until noticed

Be concrete. Reject abstract advice like "add monitoring". Specify what
metric, what threshold, what alert.

Design to review:
---
{PASTE PLAN HERE}
---
