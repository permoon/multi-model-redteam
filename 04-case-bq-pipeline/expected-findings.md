---
case: "bq-pipeline"
run_at: "2026-04-29T12:51:43Z"
plan_file: "04-case-bq-pipeline/plan.md"
models:
  claude:
    cli_version: "2.1.114 (Claude Code)"
    model: "as configured (default)"
    flags: "--print"
  codex:
    cli_version: "codex-cli 0.125.0"
    model: "gpt-5.5 (medium reasoning)"
    flags: "exec --skip-git-repo-check"
  gemini:
    cli_version: "0.36.0"
    model: "as configured (default)"
    flags: "(stdin, no flag)"
timeout_sec: 600
notes: |
  Output is non-deterministic. Findings below are from THIS specific run on
  2026-04-29; your output may differ in wording but should match the
  pattern: ~13 consensus findings, ~11 unique findings, ~3 triple-blind-spot
  items, plus disagreements and coverage gaps.

  This run captured all 7 deliberately seeded flaws in plan.md (per the
  chapter README):
    1. ANY_VALUE/MIN(event_ts) inconsistency       → C4 (Claude + Codex)
    2. NOT EXISTS subquery alias shadowing         → U1 (Claude only — the
                                                     highest-value finding)
    3. Imputed timestamp crossing partitions       → U2 (Gemini only)
    4. PG→GCS in-flight tx & timezone semantics    → C2 + C3 + U3
    5. Rerunning Step D creates duplicates         → C1 + C9
    6. Missing imputation_run_id for rollback      → C11
    7. "less than 50% of expected" ambiguity       → C12 + D2

  Highlights: U1 is the textbook example of a single-LLM blind spot — Codex
  and Gemini both *cited* the buggy SQL block but assumed it worked. Only
  Claude tested whether `WHERE m2.user_id = user_id` actually binds in
  BigQuery's scoping rules. Without multi-model review, the project's
  stated purpose (imputation) would silently no-op for 2-8 weeks.
---

## Consensus Findings (mentioned by ≥ 2 teams)

### C1. Step C `INSERT INTO order_events_dedup` is not idempotent
**Teams:** Claude (1B/4B), Codex (1.1/4.1), Gemini (4A)
**TRIGGER:** Any retry of Step C — Workflow auto-retry, manual rerun after a Step D failure, or "running it twice just to be safe."
**IMPACT:** Yesterday's rows appear 2× in the dedup table. Claude: "Dedup table no longer dedup'd. Downstream funnel counts double." Gemini: "BI users report 'conversion rates > 100%'." Codex notes the BQ job can succeed silently while Workflows believes it failed.
**DETECTABILITY:** Not caught by the 50% row-count alert (over-counts, not under). Codex proposes a `COUNT(*) − COUNT(DISTINCT key)` check; the plan has none.

### C2. Late-arriving PostgreSQL rows are permanently lost
**Teams:** Claude (1D), Codex (1.2), Gemini (2B)
**TRIGGER:** A client retry / offline-queued event with `event_ts` from a prior day is written to Postgres after that day's 02:00 UTC export. Claude's specific case: "an event with `event_ts = Monday 23:50` that arrives in Postgres on Wednesday is permanently lost."
**IMPACT:** Codex: "Legitimate orders disappear from BigQuery forever." Estimated 0.1–1% loss; concentrated in mobile retries.
**DETECTABILITY:** All three agree this is invisible from BigQuery alone. Requires Postgres↔BQ reconciliation that the plan does not include.

### C3. PostgreSQL replica lag at 02:00 UTC
**Teams:** Claude (2A), Codex (2.1), Gemini (2B)
**TRIGGER:** Step A reads from a lagging replica; final minutes of "yesterday" not yet replicated when the export runs.
**IMPACT:** Silent loss of the day's tail-end (~0.1–0.5%). Especially likely during APAC business hours, which Claude calls out: "yesterday UTC ends at start of APAC morning."
**DETECTABILITY:** Below the 50% threshold. Codex's mitigation: fail the workflow if `replica_lag_seconds > 300`.

### C4. `ANY_VALUE(source_event_id)` is non-deterministic / breaks traceability
**Teams:** Claude (1C), Codex (1.3)
**TRIGGER:** Duplicates whose copies have different `source_event_id`; dedup keeps an arbitrary one.
**IMPACT:** Claude: any "downstream join on `source_event_id` (e.g., to a fraud system or to raw event logs) silently breaks." Codex: "Debugging an order points to the wrong raw event."
**DETECTABILITY:** Months. No proposed monitoring in the plan.

### C5. CSV special characters break or silently shift columns
**Teams:** Claude (3C), Codex (3.3), Gemini (2A)
**TRIGGER:** `user_id` / `order_id` containing `,`, `"`, `\n`, or formula-prefix characters (`=+-@`).
**IMPACT:** **Note disagreement (see below):** Claude says "silent column shift" if load succeeds; Gemini says load fails loudly. Codex adds spreadsheet formula-injection risk for downstream analysts.
**DETECTABILITY:** Depends on load options (`--allow_jagged_rows`, `--max_bad_records`); not covered in plan.

### C6. Step D imputation full-table scan → cost grows linearly
**Teams:** Claude (1E), Gemini (3A)
**TRIGGER:** Every daily run after table accumulates. Step D has no date filter on the outer table.
**IMPACT:** Claude: "by month 12 each daily Step D scans ~150M rows for a 300k/day insert." Gemini quantifies: "$5/day → $500/day" and eventually exceeds the 6-hour limit.
**DETECTABILITY:** Only via `INFORMATION_SCHEMA.JOBS` bytes-billed trend. Not in monitoring plan.

### C7. Upstream `event_type` evolution silently breaks the pipeline
**Teams:** Claude (4C), Codex (2.3)
**TRIGGER:** Mobile team ships `refund`, `payment`, `Paid`, `checkout_started`, etc. Schema is `STRING NOT NULL` with no enum.
**IMPACT:** Claude: imputation's `COUNT(DISTINCT event_type) = 2` may match `(refund, paid)` and "generate spurious imputed checkouts for refunded orders." Codex: BI filters silently exclude unknown values.
**DETECTABILITY:** Same-day if a domain-check query exists; nothing in plan.

### C8. BI cutover and mid-pipeline state visibility
**Teams:** Claude (5C/4D), Codex (4.2/2.4), Gemini (5B)
**TRIGGER:** Two related cases: (a) BI repointed Monday morning before any prod run is validated for correctness; (b) dashboard refresh between Step C and Step D sees real events but missing imputed checkouts.
**IMPACT:** Claude: "stakeholders see broken funnel during the window, often during APAC morning meetings." Gemini: "executive dashboard could show a sudden funnel collapse." Codex flags absence of a `pipeline_run_status = success` gate.
**DETECTABILITY:** Plan has no readiness marker; "ephemeral — the dashboard refreshes again and looks fine" (Claude).

### C9. Backfill ticket conflicts with daily pipeline (three distinct bugs)
**Teams:** Claude (4A), Codex (4.3), Gemini (4B)
- Claude: backfill no-ops because Step C's `WHERE DATE(event_ts) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)` is hardcoded.
- Codex: if backfill reuses the same append-only insert, it duplicates any partition that already exists.
- Gemini: a backfill running concurrently with the daily run produces duplicate imputed events because Step D's `NOT EXISTS` doesn't see snapshot-isolated concurrent inserts.
**IMPACT:** Backfill either silently fails, doubles 6 months of history, or corrupts imputation. Plan explicitly defers backfill to "a separate ticket" without solving any of these.
**DETECTABILITY:** Discovered post-hoc via trend anomaly.

### C10. Bad imputation discovered after multi-day delay
**Teams:** Claude (5B), Codex (5.2), Gemini (5A)
**TRIGGER:** Logic error in Step D persists for N days before anyone notices.
**IMPACT:** Codex: "Product and revenue analytics for multiple days are wrong... blast radius becomes all partitions since launch." Recovery requires full recompute — Claude notes the cost implications, Gemini calls out Looker dashboard inconsistency.
**DETECTABILITY:** All three estimate ~5 days via ratio anomaly (`checkout_to_paid_ratio` jumps).

### C11. No `run_id` / `loaded_at` in dedup table = no safe rollback
**Teams:** Claude (5A), Codex (5.1/5.3)
**TRIGGER:** Any incident requiring deletion of one bad run.
**IMPACT:** Claude: rollback "either over-deletes (drops late-arriving good data) or under-deletes (leaves stale imputed rows)." Codex: "Add `loaded_at` / `run_id` to final before launch."
**DETECTABILITY:** Discovered during incident, never proactively.

### C12. Empty-day / retry-storm volume boundaries
**Teams:** Claude (3A/3B), Codex (3.1/3.2), Gemini (3B)
**TRIGGER:** Either zero rows (upstream outage, TZ bug, maintenance window) or 10–100× rows (mobile retry storm worsens beyond the documented 2–5×).
**IMPACT:** Claude raises alert-fatigue for legitimate empty days. Codex: "BigQuery job duration > 30 minutes... slot budget" exhaustion on storm side. Workflow step timeout becomes plausible.
**DETECTABILITY:** 50% threshold is one-sided (low only); high-volume blowup is invisible to current monitoring.

### C13. `TIMESTAMP_ADD(MIN(event_ts), INTERVAL 1 SECOND)` for synthetic checkout
**Teams:** Codex (1.4), Gemini (5A)
**TRIGGER:** The two teams diagnose **different failure modes for the same construct** — see disagreements below.
**IMPACT:** Either way: corrupted funnel ordering for imputed orders.
**DETECTABILITY:** Same-day with an ordering validation query (Codex provides one); plan has neither.

---

## Unique Findings (mentioned by 1 team)

### U1. **[Claude only]** Step D's correlated subquery has unqualified column references → imputation silently no-ops after day 1
This is the single highest-value finding in any of the three reviews.
**TRIGGER:** Any `checkout` row exists anywhere in `order_events_dedup` (always true after day 1).
**IMPACT:** Claude: "imputation works on day 1, then silently does nothing forever. Funnel reports show the same artificial drop-off the project was meant to fix" — i.e., the project's stated purpose fails silently. Worse: combined with the day-1 over-fire, launch day shows spuriously perfect conversion.
**DETECTABILITY:** Claude: "2–8 weeks" — no monitoring catches it.
**Interpretation:** Codex and Gemini both *cited* this same SQL block and analyzed downstream behavior assuming it works. Neither tested whether `WHERE m2.user_id = user_id` actually binds to the outer query in BigQuery's scoping rules. This is the classic blind spot where two reviewers replicated each other's assumption.

### U2. **[Gemini only]** Midnight boundary race conditions in dedup
**TRIGGER:** A duplicate event retried at 23:59:59 (Day 1) and 00:00:02 (Day 2). The two copies land in different daily partitions; Step C's GROUP BY operates only within yesterday's staging, so dedup never sees them together.
**IMPACT:** Two records retained for the same logical event, inflating purchase intent metrics.
**DETECTABILITY:** Low — counts look normal. Requires a cross-partition uniqueness check.
**Interpretation:** Genuine insight. Claude's 1E touches cross-day for *imputation cost*, not dedup correctness. Codex doesn't address this. The bug exists if the dedup happens within yesterday's partition only.

### U3. **[Gemini only]** Timezone / DST shift between Postgres and BigQuery
**TRIGGER:** Postgres server (or export script) uses local time while BQ defaults to UTC.
**IMPACT:** "7–8 hour data gap or 7–8 hours of double-counted data."
**DETECTABILITY:** Caught only if shift exceeds the 50% threshold.
**Interpretation:** Real concern in any cross-region pipeline; the other two teams missed it.

### U4. **[Codex only]** GCS CSV export truncated, BQ load succeeds anyway
**TRIGGER:** Export job partial due to timeout / disk pressure / pagination bug; CSV ends mid-file but is still syntactically valid.
**IMPACT:** Up to ~50% silent data loss can pass the row-count alert. Codex proposes Postgres↔GCS↔BQ tri-count reconciliation.
**DETECTABILITY:** Same-day only with the proposed reconciliation; plan has none.
**Interpretation:** Strong unique insight. Claude's 1D and Gemini's 2B address late-arrivals on the *source* side; only Codex flags the *transport* side.

### U5. **[Codex only]** Extremely long `user_id` strings degrade clustering
**TRIGGER:** 10KB or junk-cardinality IDs from upstream.
**IMPACT:** Load size and query cost increase; clustering loses effectiveness; Looker dashboards slow.
**DETECTABILITY:** Easy with length-distribution check; not in plan.
**Interpretation:** Niche but specific.

### U6. **[Codex only]** Analyst forgets to filter `is_imputed`
**TRIGGER:** BI explores built without exposing or filtering the column.
**IMPACT:** "Product teams may believe checkout UX improved when only imputation changed the funnel" — i.e., the metric *the project exists to fix* becomes a misleading metric.
**DETECTABILITY:** "Days later in metric review."
**Interpretation:** Sociotechnical finding the other two missed. Combined with U1, this is doubly dangerous.

### U7. **[Codex only]** Replace-mode staging destroys forensic evidence
**TRIGGER:** A bad export overwrites the previous good staging contents.
**IMPACT:** Cannot diff failed run vs prior good run inside BQ; debugging depends on GCS retention.
**DETECTABILITY:** Same-day only via row-count delta vs 28-day baseline.
**Interpretation:** Operational gap; Claude 5A and Gemini 5B touch rollback but not staging forensics.

### U8. **[Claude only]** Email-only alerting → Friday→Monday silent failure
**TRIGGER:** Workflow fails Friday 02:00 UTC; email lands in shared inbox; no PagerDuty / Slack / ack.
**IMPACT:** "BI dashboards stale through Monday morning."
**DETECTABILITY:** 60–72 hours.
**Interpretation:** Operational reality the others assumed away.

### U9. **[Claude only]** Watcher-of-watcher: the 50% scheduled query is itself unmonitored
**TRIGGER:** GCP pauses scheduled queries after consecutive failures; nothing watches the watcher.
**IMPACT:** "Data quality alerting silently disabled."
**DETECTABILITY:** Indefinite.
**Interpretation:** Claude is the only team thinking about meta-monitoring.

### U10. **[Claude only]** PII / GDPR deletion completeness with imputed rows
**TRIGGER:** Article 17 deletion request post-launch.
**IMPACT:** Imputed `checkout` rows have synthetic `source_event_id` — deletion-completeness audits become hard.
**DETECTABILITY:** Only on audit; months to years.
**Interpretation:** Compliance dimension neither other team raised.

### U11. **[Claude only]** `event_ts` as NULL or epoch 0
**TRIGGER:** Client bug, dev test data leaking to prod, manual SQL backfill leaving NULLs.
**IMPACT:** Phantom partitions like `0001-01-01` break partition pruning across all consumers.
**DETECTABILITY:** Silent under typical load options.

---

## Apparent Disagreements

### D1. CSV special-character handling: silent corruption vs loud failure
- Claude (3C): "silent if load succeeds. Caught only when a downstream NULL check or value enum check fires. Usually never."
- Gemini (2A): "High [detectability]. Cloud Workflows will fail. Alert: `workflow_status == 'FAILED'`."
- The truth depends on load-job options (`--allow_jagged_rows`, `--max_bad_records`, `--quote`), which the plan does not specify. Humans must resolve which mode the plan actually uses.

### D2. Existing 50%-row-count alert: too sensitive, just right, or too late?
- Claude (3B): "alert email fires. Operator silences it. Real low-volume failures get habituated-away" — alert fatigue.
- Gemini (3B): "High [detectability]. The 'less than 50% of expected' alert will trigger" — alert is sufficient.
- Codex (3.1): catches it "only after scheduled row-count check, not necessarily before BI switch" — alert is too late.
- All three views are partially valid. Humans must decide whether the alert is the right instrument at all.

### D3. Failure mode of `INTERVAL 1 SECOND` in synthetic checkout
- Codex (1.4): synthetic checkout is "placed one second after `paid`" because clock skew makes `MIN(event_ts)` be `paid` itself → "funnel ordering invalid."
- Gemini (5A): "INTERVAL 1 SECOND causes a collision with a real event" → duplicate timestamps.
- Different bugs diagnosed in the same line. Humans must check the actual data distribution: is clock-skew the realistic case, or are 1-second-resolution collisions?

### D4. Severity of replica lag
- Claude (2A): "0.1–0.5% of daily volume" — tolerable if reconciliation is added later.
- Gemini (2B): "rows are lost to BigQuery forever" — frames as data loss requiring reconciliation script.
- Codex (2.1): proposes failing the workflow at `replica_lag_seconds > 300` — strict gating.
- Spans tolerate→reconcile→hard-fail. Humans must choose policy.

---

## Coverage Gaps

All five top-level frame dimensions had ≥9 concrete scenarios across the three teams, so none are *thin* at the top level. The thin sub-areas:

- **Authentication & secrets management** (0 scenarios). How does Workflows authenticate to Postgres? Service-account scope, secret rotation, blast radius if compromised — no team raises any of this.
- **GCS object lifecycle / forensic retention** (1 partial: Codex U7). What is the bucket retention? If 7 days, replay older runs is impossible.
- **BigQuery quotas** (0 scenarios). DML quotas during a partition-spanning recovery DELETE; concurrent-query quotas during incident; slot reservation behavior under storm.
- **Looker cache / downstream invalidation** (0 scenarios). When data is corrected, downstream caches and derived tables aren't refreshed. Codex 4.4 touches the `is_imputed` filter but not cache state.
- **Schema drift on the column dimension** (0 scenarios). All teams flag *value* drift (event_type), but not *column* drift (Postgres adds a column → CSV has N+1, BQ load expects N).
- **Concurrency between daily run and ad-hoc queries** (1: Gemini 4B for backfill only). Analyst-initiated `DELETE`/`UPDATE` against the dedup table during a run isn't covered.

---

## Triple Blind Spot

Three items I'm confident all three teams missed. Conservatively flagged.

### B1. Authentication & secrets between Workflows and PostgreSQL
**TRIGGER:** Any production launch must specify how Step A authenticates to the source DB. Standard concerns: where the credential is stored, who can read it, rotation cadence, blast radius if the service account is compromised.
**IMPACT:** A single leaked credential exposes the source-of-truth analytics DB. Rotation is plausibly never planned given nothing in the plan mentions it.
**DETECTABILITY:** Compromise is detectable only via Postgres audit logs, which aren't part of this pipeline's monitoring.
**Why I'm confident:** Three reviewers covering "what could go wrong" should hit auth/IAM at least once across 50+ scenarios. None did. The launch checklist almost certainly omits credential rotation.

### B2. Schema drift on the *column* dimension (not just values)
**TRIGGER:** Postgres team adds a `device_type` column to the source events table. Step A's `SELECT *` (or column list out of sync) → CSV has N+1 columns. BQ load with default options either fails loudly OR with `--allow_jagged_rows` succeeds and shifts data.
**IMPACT:** Either pipeline halts (loud), or columns silently shift one position and `event_ts` ends up parsed as a string, then partition column gets garbage.
**DETECTABILITY:** Depends entirely on load options not specified in the plan.
**Why I'm confident:** Claude 3C, Codex 3.3, Gemini 2A all stop at *character* escaping inside cells. Codex 2.3 covers *value* drift in `event_type`. None covers column-count drift. This is the textbook CSV-load failure mode.

### B3. BigQuery DML quota exhaustion during recovery
**TRIGGER:** A recovery `DELETE FROM order_events_dedup WHERE is_imputed = TRUE AND event_ts > '5 days ago'` (Gemini's exact recovery prescription) hits BQ's per-table DML rate limits when spread across many partitions.
**IMPACT:** Recovery itself fails or takes hours longer than expected; on-call is forced to invent a CTAS-rebuild path mid-incident.
**DETECTABILITY:** Discovered during incident.
**Why I'm confident:** All three teams *prescribe* DML-based recovery (`DELETE WHERE is_imputed`, partition DELETE, etc.) without checking that BQ actually supports the cardinality they assume. This is a known operational gotcha none of them surfaced.
