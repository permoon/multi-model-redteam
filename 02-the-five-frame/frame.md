# The 5-failure-dimension red team frame

The methodological core of `multi-model-redteam`. Read the prompt at
[`../prompts/system-prompt.md`](../prompts/system-prompt.md) first; this
file explains *why* it's shaped this way.

## The 5 dimensions

A red-team review must cover all five. For each, demand AT LEAST 2
concrete failure scenarios — abstract advice ("add monitoring") is
explicitly rejected.

### 1. Hidden assumptions

What does the design *implicitly* depend on, but never state?

Common axes:
- **Ordering**: messages arrive in send order, jobs run in submit order
- **Uniqueness**: IDs don't repeat, names don't collide
- **Atomicity**: `read → modify → write` is a single step
- **Data freshness**: caches are coherent, replicas are caught up
- **Caller behavior**: callers retry, callers respect the contract

### 2. Dependency failures

What breaks when an upstream / downstream dependency degrades?

Distinct from "downtime" — degraded means *partially working*:
- 5-minute outage (handle with retry)
- 5-hour outage (handle with backpressure or human escalation)
- p99 latency 10× normal (timeouts cascade)
- intermittent 5xx errors (retry storm risk)

### 3. Boundary inputs

What happens at p99 and at malicious-percentile inputs?

- Empty input
- Single-element input
- Huge batch (10× p99)
- Malformed (truncated, encoding-broken)
- Malicious (deliberately weaponized)
- Adversarial timing (e.g., bursts at minute boundaries)

### 4. Misuse paths

What if humans don't follow the plan? Three sub-cases:
- **Caller** misbehavior: future PRs wire the API wrong
- **User** behavior: end users skip steps, retry too soon, etc.
- **Operator** behavior: SRE scales horizontally, CI deploys 5× per hour

### 5. Rollback & blast radius

How do you recover, and how big is the damage?

- **Rollback procedure**: who runs what command, in what time
- **Blast radius**: how many users / servers / regions affected
- **Detectability**: 5-minute alert, or 5-day silent corruption?
- **Reversibility**: data corruption vs config glitch

## Why these 5, not OWASP / SRE

| Frame | Focus | Why we don't use it |
|---|---|---|
| OWASP Top 10 | Security vulnerabilities | Too narrow — misses ops & data |
| SRE Four Golden Signals | Operational health (latency / traffic / errors / saturation) | Only useful *after* deploy; design review needs a pre-deploy lens |
| **5-failure-dimension** | **Pre-deploy design review** | **Targets the design-stage ops, data, and IAM failures the frames above tend to miss** |

The 5 dimensions are the things most often missed *between* code completion
and deploy. By the time SRE signals fire, the design is already in
production.

## Calibration: bad prompt vs good prompt

❌ **Bad prompt** (what most people try first):

> Review this design and tell me what could go wrong.

This produces "add monitoring", "use retry", "consider edge cases" —
abstract advice with no actionable form.

✅ **Good prompt** (this repo's frame):

> 5 dimensions × ≥ 2 concrete scenarios each × {TRIGGER, IMPACT, DETECTABILITY}.
> Reject abstract. Specify metric / threshold / alert.

This forces the model to:
1. **Cover all 5 dimensions** (no cherry-picking the easy ones)
2. **Be concrete**: each scenario must have a reproducible trigger
3. **Reason about severity**: detectability implies SLO thinking

## Good finding vs bad finding

| Dimension | 🔴 Bad finding (abstract, unactionable) | 🟢 Good finding (concrete, actionable) |
|---|---|---|
| Hidden assumptions | "Design assumes user_id is unique." | "Design assumes user_id stays unique across PostgreSQL → BQ migration. If a user is deleted then re-registered, BQ dedup silently merges old + new identity. TRIGGER: re-registration. IMPACT: cross-identity data bleed. DETECTABILITY: outlier query on score distribution — months." |
| Dependency failures | "API might fail." | "Vertex AI batch API has 60s p99 latency in `us-central1`; this Workflow has 30s timeout, so 5–10% of imputation calls fail silently. TRIGGER: any batch > 200 events. IMPACT: imputation skip without alert. DETECTABILITY: downstream coverage check — days." |
| Boundary inputs | "Big batches might break." | "BigQuery INSERT has implicit row size limit; if any single user has > 50k events in 24h (bot/scrape), dedup INSERT fails and whole day's imputation rolls back. TRIGGER: 0.01% of days. IMPACT: 24h data loss. DETECTABILITY: Workflow alert — minutes." |
| Misuse paths | "User might call wrong order." | "Step C (dedup) and Step D (imputation) are independent BQ jobs. If operator manually re-runs Step D after Step C failed, imputation runs on stale data. TRIGGER: operator manual rerun. IMPACT: silent data bloat. DETECTABILITY: weekly QA query." |
| Rollback / blast radius | "Need to handle errors." | "Imputation has no `imputation_run_id` column; if logic ships buggy, rollback = `DELETE WHERE is_imputed = TRUE` for the day, which collides with future re-runs. TRIGGER: imputation regression. IMPACT: 1-day data loss + 30 min manual recovery per incident. DETECTABILITY: rare." |

Rule: **a good finding can be written as a ticket** — PM reads it, knows
exactly what to do. A bad finding is a vibe.

## 10-minute calibration rubric

After the model produces findings, walk through this checklist for each
one. **5 checked = MUST-FIX candidate. < 4 checked = reject and rewrite.**

- [ ] Concrete TRIGGER (not "if something goes wrong")
- [ ] Concrete IMPACT (who, how badly, quantifiable)
- [ ] Concrete DETECTABILITY (time unit: minutes / hours / days / never)
- [ ] Not generic advice (no "add monitoring" / "use retry" / "consider X")
- [ ] Writable as a ticket (PM reads it and knows what to do)

This rubric runs *before* severity ranking ([Chapter 06](../06-going-further/)
covers severity). Filtering bad findings here saves your reviewers' time.

## Common pitfalls

- **Wanting to expand to 7 / 8 dimensions**: tempting but resist. Use the
  current 5 on 20 cases; if you genuinely need a 6th (e.g., "compliance"
  in a regulated industry), add it. Don't pre-emptively bloat the frame.
- **LLMs default to generic advice**: the prompt's "Reject abstract.
  Specify metric / threshold / alert" line is mandatory. Removing it
  collapses output quality immediately.
- **Don't run the rubric mentally**: write a small script that pattern-
  matches "add monitoring" / "consider X" and flags those findings for
  rewrite. The rubric is most valuable when automated.

## Where this came from

This frame is what I (Hector) ended up with after running multi-LLM
reviews on ~15 design docs across BigQuery pipelines and GCP deploys at
ValueX. Earlier versions had 7 dimensions (compliance + observability
were separate); I collapsed them because they always co-occurred with
the existing 5. If your domain genuinely needs them split, fork the
prompt — it's CC0 for exactly this reason.

[← Back to chapter README](./README.md)
