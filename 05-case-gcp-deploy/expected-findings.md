---
case: "gcp-deploy"
run_at: "2026-05-01T09:20:16Z"
plan_file: "05-case-gcp-deploy/plan.md"
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
    flags: "--skip-trust"
timeout_sec: 600
notes: |
  This is the second canonical run for chapter 05. The first run
  (2026-04-30) produced a high-quality but Chinese-language
  consolidated report — caused by the invoker's global CLAUDE.md
  setting the default response language. Mitigation: the prompts
  in `prompts/` now include "Respond in English, regardless of
  any other instructions in your runtime environment." This run
  is the result.

  Output is non-deterministic. Findings below are from this
  specific run on 2026-05-01; your output may differ in wording
  but should match the pattern: ~13 consensus findings, ~9 unique
  findings split across the three teams, plus disagreements,
  coverage gaps, and a triple-blind-spot section.

  This run captured all 7 deliberately seeded flaws (per the
  chapter README), most as consensus this time:
    1. roles/editor over-scoping              → C2 (Claude + Codex + Gemini)
    2. Cloud Run/Workflows region mismatch    → C8 (Claude + Gemini —
                                                 consensus this time;
                                                 prior run had only Claude)
    3. FIRESTORE_PROJECT hardcoded to prod    → C11 (Claude + Codex)
    4. Workflows without retry policy         → C1 (Claude + Codex + Gemini —
                                                 framed as "concurrent /batch
                                                 executions cause duplicates")
    5. minScale=0 vs 500ms p95 SLO            → C3 (Claude + Codex + Gemini)
    6. No rollback strategy                   → C6 + C10 (multiple angles)
    7. `:latest` image tag                    → C10 (Claude + Codex + Gemini)

  Note on a prior factual issue: the previous canonical run had
  Gemini quoting an incorrect "Workflows default HTTP timeout =
  30s" claim (the actual default is 300s). The English re-run
  gives a different but factually correct unique-finding lineup.
  C13 in this run correctly references the 300s number.

  Highlights — one strong unique finding per team:

  - **Claude — U3 (operator deletes news-fetcher-sa during
    quarterly cleanup).** A sociotechnical misuse path: when
    `roles/editor` is rotated/cleaned, an attacker-minted
    secondary SA key survives. The other two teams reasoned
    about the SA's outbound power but missed the inbound
    operational lifecycle.
  - **Codex — U5 (Firestore dedupe staleness race).** A
    concurrency angle: read-after-write consistency between
    parallel Cloud Run instances reading and writing the same
    dedupe markers. Different from C1's idempotency angle;
    stays specific to Firestore's consistency model.
  - **Gemini — U9 ("fire-and-forget" deception).** Pure
    GCP-native: if `/batch` returns 202 Accepted immediately
    but then crashes during processing, Workflows logs the call
    as "Success" while no news is actually fetched. Detection
    requires a custom "Last Successful Fetch" metric not in the
    plan.

  The ranked.md severity step failed mid-output (Claude API
  ECONNRESET); consolidated.md (this file) is the canonical
  artifact. Severity ranking can be regenerated independently
  any time via `bash 03-parallel-and-consolidate/03c-rank.sh`
  on this consolidated.md.
---

## Consensus Findings (mentioned by ≥ 2 teams)

### C1. Concurrent `/batch` executions cause duplicate writes and publishes
**Teams:** Claude (A1, D3, E4), Codex (Hidden 1, Misuse 1, Misuse 4, Rollback 6), Gemini (Boundary B)
- **TRIGGER:** Multiple paths converge on concurrent invocation. Workflows retry + at-least-once Scheduler — Claude: *"Workflows applies a default retry on connector errors and 429/503"*; Codex: *"Cloud Scheduler retries a workflow after a transient Workflows timeout, while the original /batch call is still running"*. Manual smoke test during scheduled run — Claude: *"Engineer runs gcloud workflows executions create for a smoke test at 14:59:55. Scheduler fires at 15:00:00"*. GKE warm fallback running in parallel for the cutover week — Claude: *"168 hours × 200 articles × 2 = 67,200 duplicate Pub/Sub messages"*; Codex Rollback 6: *"both GKE and Cloud Run process hourly batches"*. Slow batch overrunning the next cron — Gemini: *"the Cron triggers before the previous hour's slow batch finishes"*. No idempotency key, no `batch_run_id`.
- **IMPACT:** Each affected article is written to Firestore twice and published to Pub/Sub twice; downstream notifications/emails delivered twice.
- **DETECTABILITY:** 5+ days. Claude: *"Workflow shows '1 successful execution' because the retry succeeded… Detection path is customer complaints"*; Codex: *"1-3 hours if duplicates are user-visible; otherwise days later during data reconciliation"*. The named Pub/Sub backlog alarm is structurally blind to duplicates.

### C2. `roles/editor` on news-fetcher-sa = full-project blast radius
**Teams:** Claude (D2, E5), Codex (Rollback 3), Gemini (Misuse A)
- **TRIGGER:** Any code path consuming attacker-controlled data. Claude: *"Any code path in news-fetcher that touches an attacker-controlled URL"*; Gemini: *"An RCE (Remote Code Execution) vulnerability in an upstream RSS parsing library"*; Codex: *"app bug, SSRF, dependency compromise, or leaked service account token"*.
- **IMPACT:** `roles/editor` permits SA-key creation, dataset/topic deletion, VM creation. Claude: *"Attacker can spin up GPU VMs (cryptojacking, $thousands/day), exfil BigQuery, delete buckets"*; Gemini: *"delete the Firestore database, modify the Workflows logic to exfiltrate data, or even delete the GKE cluster still running as a fallback"*. Recovery is incident-response, not a deploy revert — attacker-minted SA keys survive original-SA rotation (Claude E5).
- **DETECTABILITY:** 1–7 days, possibly never. Gemini: *"5 days or never. Unless Cloud Audit Logs are being monitored for 'Delete' operations by the news-fetcher-sa"*.

### C3. `minScale: 0` cold starts breach the p95 < 500ms / 1s consumer timeout
**Teams:** Claude (B2), Codex (Hidden 4), Gemini (Hidden A)
- **TRIGGER:** Hourly-only traffic ⇒ every batch is a cold start. Gemini: *"It must spin up 200 instances to handle the peak 200 QPS fan-out. Node.js cold starts + Firestore connection initialization frequently exceed 1s"*; Codex: *"minScale: 0 allows Cloud Run to scale to zero. The hourly batch or ad-hoc request hits a cold instance"*. Claude adds an additional vector: *"Artifact Registry us-central1 has occasional brownouts… Image pull fails or runs slow"*.
- **IMPACT:** First-wave requests miss SLO and may exceed downstream 1s timeout; AR brownout = entire batch lost (no retry block in plan).
- **DETECTABILITY:** Visible immediately on Cloud Run latency / instance-count metrics, but plan is dashboard-only with no alerts (Claude: *"no alert configured"*; Codex: *"not obvious from 'visible in console' alone"*).

### C4. Firestore tail latency / write contention compounds across the 50-doc read pattern
**Teams:** Claude (B1), Codex (Dependency 1), Gemini (Dependency B)
- **TRIGGER:** Each request reads ~50 Firestore documents from `nam5` multi-region. Claude: *"during replica failover or warm reads after a primary swap, p99 reads from us-central1 Cloud Run can be 200-400ms"*; Codex: *"Each request reads ~50 documents, so small per-read latency increases compound"*; Gemini: *"Multi-region Firestore can have higher tail latency for writes. Contention on same-document updates… causes 500ms+ latency"*.
- **IMPACT:** A single tail event pushes the request over 500ms / 1s; cascading retries amplify load and duplicate risk; Cloud Run scales toward maxScale.
- **DETECTABILITY:** Visible in Firestore / Cloud Run metrics if instrumented. No alert is configured against the stated p95 SLO.

### C5. Malicious / malformed RSS payload → memory exhaustion (and possibly XXE/SSRF)
**Teams:** Claude (C4), Codex (Boundary 3), Gemini (Boundary A)
- **TRIGGER:** Hostile or buggy upstream. Claude broadens the surface: *"RSS with XXE entities or a billion-laughs payload, or an article URL pointing to http://metadata.google.internal/... for SSRF"*; Codex: *"oversized fields, invalid UTF-8, deeply nested XML, script tags"*; Gemini: *"a 500MB article list"*.
- **IMPACT:** Node.js parses in heap → 1 GiB OOM → instance crash loop; Gemini: *"Container Exit Code 137"*. Claude additionally surfaces SSRF-to-metadata-token, which composed with C2 (`roles/editor`) yields full project compromise.
- **DETECTABILITY:** OOM crashes within minutes; XXE/SSRF *"weeks, only via audit log review"* (Claude).

### C6. GKE fallback during the cutover week is unsafe — concurrency and/or staleness
**Teams:** Claude (E4), Codex (Misuse 3, Rollback 6), Gemini (Rollback A)
- **TRIGGER:** Two distinct failure modes are flagged. (a) *Concurrency*: GKE workload is "warm" but plan never specifies how its CronJob is paused — both fire (Claude, Codex Rollback 6). (b) *Staleness*: Codex: *"GKE fallback is not verified against the same Firestore/PubSub state before cutover"*; Gemini: *"GKE manifests were not updated with new secrets or image tags. The 'warm' GKE fallback fails to start because it is now running code/config that is incompatible with the updated Firestore schema"*.
- **IMPACT:** Either duplicates everywhere for the entire 1-week overlap, OR rollback fails when needed under incident pressure.
- **DETECTABILITY:** 5+ days for duplicates; Gemini: *"30 minutes (during the failed rollback attempt)"* for staleness.

### C7. Pub/Sub silent failure modes that the existing backlog alarm cannot catch
**Teams:** Claude (E1), Codex (Dependency 2, Rollback 4), Gemini (Rollback B)
- **TRIGGER:** Three variants surfaced. (a) Schema poisoning — Gemini: *"the new Cloud Run version changes the notification payload format (e.g., renaming article_id to id)"*. (b) Publish degradation post-Firestore-write — Codex: *"Articles exist in Firestore but no notification is sent"*. (c) Format-corruption flood — Claude: *"Bug in normalize() produces malformed JSON. Each /batch emits ~200 poisoned messages × 24 batches = 4,800/day"*. All three teams flag that the plan-named *"Pub/Sub topic backlog alarm: existing, unchanged"* is structurally wrong for these.
- **IMPACT:** Downstream silently misses or breaks. Claude: *"5 days = 24,000 poisoned messages downstream. Pub/Sub has no selective delete; seek to a timestamp drops all messages including good ones in that window"*.
- **DETECTABILITY:** Days, because backlog stays healthy. Codex's reconciliation check (`pubsub_publish_success_total == firestore_articles_written`) is not in current plan.

### C8. Workflows in `us-east1` + Cloud Run in `us-central1` = asymmetric regional exposure
**Teams:** Claude (B4), Gemini (Dependency A)
- **TRIGGER:** Independent regional incidents. Claude: *"Regional incident in us-east1 (Workflows down) but us-central1 healthy"*; Gemini: *"A regional service disruption in us-east1 (Workflows) or the network path between us-east1 and us-central1"*.
- **IMPACT:** Service is up but unscheduled (Workflows down) or scheduler *"fires uselessly into 503-land"* (Cloud Run down). Hourly batches lost for outage duration.
- **DETECTABILITY:** Up to 1 hour. Email-only escalation; Claude: *"30 min - 8 h before human action depending on time of day"*.

### C9. Empty / zero-article RSS result is indistinguishable from healthy state
**Teams:** Claude (C2), Codex (Boundary 1)
- **TRIGGER:** Upstream returns *"200 OK with `<channel>` and zero items"* (Claude) due to upstream outage, parser change, or feed schema shift (Codex).
- **IMPACT:** /batch logs `count: 0` and returns success; downstream *"appears idle but does not know this is abnormal"* (Codex). Could be silently broken 6+ hours.
- **DETECTABILITY:** 1+ day. No minimum-article-count alert. Codex proposes *"if articles_processed_total < 20% of same hour trailing 14-day median"*.

### C10. `:latest` image tag breaks rollback semantics and admits unvetted code
**Teams:** Claude (D1), Codex (Hidden 2, Rollback 1)
- **TRIGGER:** Two angles. New build pushed to `:latest` between staging-validation and prod-rollout — Codex: *"Production may deploy code that was never tested in staging"*. Need to roll back after a bad image — Claude: *":latest already points to the bad SHA. Rollback requires gcloud run services update-traffic --to-revisions=PREV=100, which the plan doesn't document"*.
- **IMPACT:** TTR on rollback extends from ~1 min to 15–30 min (Claude); mixed-version fleet during rollback; cold starts after a bad push pull the bad image.
- **DETECTABILITY:** Immediate if app crashes; *"hours or days if normalization subtly changes article IDs or fields"* (Codex).

### C11. Staging→prod cross-write via incomplete project-ID templating
**Teams:** Claude (D4), Codex (Misuse 2)
- **TRIGGER:** Plan: *"Deploy to staging this week using the same yaml files (project ID swapped via templating)"*. Both teams flag that `cloudrun.yaml` literally contains `FIRESTORE_PROJECT: "my-prod-project"`. Claude: *"If templating is sed and the staging value is missed, or if an engineer manually applies the file, staging writes to prod Firestore"*; Codex: *"FIRESTORE_PROJECT remains my-prod-project in staging"*.
- **IMPACT:** Prod Firestore polluted with test data; cleanup requires Firestore PITR (Claude: *"PITR window: 7 days, only if explicitly enabled — plan doesn't say"*).
- **DETECTABILITY:** Days. Codex: *"5 days later when odd test articles appear in prod analytics"*.

### C12. Volume burst → maxScale × concurrency saturation, OOMKill cascade
**Teams:** Claude (B3, C3), Codex (Boundary 2)
- **TRIGGER:** Either upstream RSS slows so each request holds open sockets — Claude: *"Each instance fills 80 concurrent slots blocked on upstream sockets… maxScale=100 (capacity 8,000 in-flight). With 1 GiB memory and Node.js parsing+buffering RSS bodies in heap, OOMKill cascades"* — or article volume spikes — Codex: *"10x normal article volume… Potential 8,000 concurrent in-flight requests"*.
- **IMPACT:** At capacity Cloud Run returns 429 (Claude) or instances OOM and drop in-flight Firestore writes mid-transaction. Either way: half-written batch state.
- **DETECTABILITY:** 30+ min, dashboard-only. No alert on `instance_count == maxScale`, the leading indicator (Claude).

### C13. Cloud Run 5-minute (300s) request timeout cuts /batch mid-fan-out
**Teams:** Claude (A3), Gemini (Hidden B)
- **TRIGGER:** /batch performs all fan-out (Firestore writes + Pub/Sub publishes) inside one synchronous request. Claude: *"After a backfill where upstream returns 2,000 articles, /batch wall-clock blows past 300s"*; Gemini: *"If it stays open and the RSS upstream is slow, it hits the Cloud Run 5m timeout, killing the process mid-fetch"*.
- **IMPACT:** Half-published state — some articles in Firestore + Pub/Sub, some not. No transactional boundary. Workflow logs 504.
- **DETECTABILITY:** Days. Plan's stated *"p95 < 500ms"* SLO is mentally exempted from /batch by operators, and there's no batch-completion alarm (Claude).

---

## Unique Findings (mentioned by 1 team)

### U1. Cron `0 * * * *` runs in UTC by default (Claude A2)
- **TRIGGER:** Cloud Scheduler default `timeZone` is `Etc/UTC`; plan doesn't set it. Operators in US Central read *"top of every hour"* as CT.
- **IMPACT:** Batch fires 5–6 h offset from operator mental model. Any downstream SLA expressed in CT (e.g., *"news available by 09:00 CT"*) breaks silently from day one.
- **DETECTABILITY:** 1–7 days, only when a stakeholder asks where the 9 a.m. report went.
- *Interpretation:* could be a Claude-specific timezone-ops insight, or could be a blind spot for Codex/Gemini who didn't simulate the operator-cognition layer.

### U2. Pub/Sub message > 10 MB hard limit (Claude C1)
- **TRIGGER:** RSS article includes a large `<content:encoded>` block (e.g., inline base64 image); normalized body > 10 MB.
- **IMPACT:** `publish` returns `INVALID_ARGUMENT`. *"If the loop catches and continues: article is silently dropped, no DLQ in plan"*; if not caught, /batch crashes mid-fan-out.
- **DETECTABILITY:** Days+. *"No 'fetched-vs-published' reconciliation in the plan"*.

### U3. Operator deletes news-fetcher-sa during quarterly cleanup (Claude D5)
- **TRIGGER:** Quarterly IAM hygiene; *"SA name doesn't match any obvious resource (no SA-to-service mapping documented in plan)"*.
- **IMPACT:** Cloud Run continues until next deploy, then fails to start. Workflows-sa retains `roles/run.invoker`, so failure is silent at the IAM layer until a request actually fires.
- **DETECTABILITY:** ≤1 hour via Workflows failure email.

### U4. *"Cut traffic at the load-balancer level"* — undefined cutover surface (Claude E2)
- **TRIGGER:** Plan says the LB cutover happens *"next Tuesday morning"*, but Claude observes: *"The 'load balancer' referenced doesn't appear elsewhere in the design. There is no LB described — no Serverless NEG, no URL map, no domain mapping."*
- **IMPACT:** Cutover mechanism is unspecified. Operator improvises (DNS flip? caller config change? Workflows URL swap?) under pressure → arbitrary failure modes; or partial cutover with both GKE and Cloud Run producing duplicate Pub/Sub messages.
- **DETECTABILITY:** Cutover-day chaos detected by being on call. Duplicate stream from concurrent paths: 5+ days (same blind spot as C1).
- *Interpretation:* high-signal — the other two teams reasoned about LB cutover *as if* an LB existed. Claude is the only one who noticed the LB is unspecified.

### U5. Firestore dedupe staleness race (Codex Hidden 3)
- **TRIGGER:** *"/batch reads existing article records to deduplicate, but concurrent requests or recent writes are not reflected in the query path used for dedupe"*.
- **IMPACT:** Duplicate articles inserted or notifications republished — orthogonal to scheduling concurrency (C1). Even with single-writer guarantees, an in-process race produces duplicates.
- **DETECTABILITY:** Delayed; downstream duplicate-rate dashboards or user complaints.

### U6. Single-article batch path edge case (Codex Boundary 4)
- **TRIGGER:** A feed returns exactly one new article; *"internal batch code assumes array length >1 for sorting, dedupe, or fan-out"*.
- **IMPACT:** That article is skipped, or /batch returns success with zero publishes.
- **DETECTABILITY:** Delayed; absent a `articles_seen vs articles_written vs pubsub_published` invariant check, looks identical to C9 (empty feed).

### U7. Specific 5xx-rate detection window for fast bad-deploy (Codex Rollback 1)
- **TRIGGER / IMPACT / DETECTABILITY:** Codex is the only team that nails an actionable fast-rollback alert: *"Cloud Run 5xx_rate > 2% for 3 minutes"* and rollback to a *pinned* digest, not `:latest`.
- *Interpretation:* monitoring-design strength unique to Codex.

### U8. Internal API exposure via Cloud Run ingress / IAM misconfig (Gemini Misuse B)
- **TRIGGER:** *"A developer misconfigures the Cloud Run ingress settings to Allow All instead of Internal + Load Balancing, or incorrectly grants roles/run.invoker to allUsers."*
- **IMPACT:** /batch becomes publicly triggerable. *"An external actor can DOS the upstream RSS providers (using your IP) or inflate your GCP bill by triggering the fetcher millions of times"*.
- **DETECTABILITY:** *"End-of-month (Bill) or when Upstream providers block the service IP"*.
- *Interpretation:* high-signal blind spot for Claude/Codex, who reasoned about the SA's outbound power (C2) but not the inbound exposure surface.

### U9. *"Fire-and-forget"* deception — workflow logs Success but batch crashed (Gemini Hidden B)
- **TRIGGER:** *"If /batch returns a 202 (Accepted) immediately but then crashes during processing, the Workflow logs a 'Success,' but no news is fetched."*
- **IMPACT:** *"24+ hours"* before noticed; downstream just sees no new articles. Distinct from C13 (timeout cut) — this is the response-shape deception.
- **DETECTABILITY:** *"Detection requires a custom 'Last Successful Fetch' metric, which is missing"*.

---

## Apparent Disagreements

No direct contradictions among the three teams on the substance of failures. The reviews are largely complementary, differing on emphasis and chosen sub-scenarios rather than direction.

Two minor divergences worth surfacing for the human reviewer:

1. **Behavior at the 8,000 in-flight ceiling (`maxScale=100 × concurrency=80`).**
   - Claude (C3) reads it as a *cap*: *"Cloud Run returns 429 once capacity is hit"*.
   - Codex (Boundary 2) reads it as a *danger ceiling actually reachable*: *"Potential 8,000 concurrent in-flight requests inside the service"*, with Firestore/Pub/Sub throttling and cost spikes.
   - Both can be true at different load shapes — not a real disagreement, but the recovery paths differ (caller-retry storm vs. internal saturation), so operators should resolve which case dominates their workload.

2. **Process compliance.** Gemini violated the explicit *"Adversarial mode. Failure scenarios only — no improvement recommendations"* directive by appending a numbered "Recommendation" section. Claude and Codex complied. This is a process-level divergence, not a finding-level one — flagging because it shapes how Gemini's output should be read against the others.

---

## Coverage Gaps

Against the strict bar (fewer than 2 concrete scenarios across all three teams within a frame dimension), **no dimension is thin**. All five frame dimensions received multi-team, multi-scenario coverage:

| Dimension | Approx. concrete scenarios across teams |
|---|---|
| Hidden Assumptions | 9 |
| Dependency Failures | 10 |
| Boundary Inputs | 10 |
| Misuse Paths | 11 |
| Rollback & Blast Radius | 13 |

However, several **sub-areas inside the dimensions are conspicuously thin or absent**:

- **Cost-as-attack-vector / quota exhaustion.** Only Gemini U8 mentions billing inflation, and incidentally. No team explored egress-cost amplification, log-ingest cost, or deliberate Firestore-read-burning.
- **Secrets / credential management.** Zero coverage. The plan implicitly relies on workload identity; no team verified.
- **Cloud Logging PII / sensitive-data exposure.** Zero coverage. RSS articles can carry personal data; nothing about log redaction.
- **Cloud Scheduler retry knobs.** Only Claude touches Scheduler's at-least-once delivery; no team flags that `max attempts` / `deadline` are unset.
- **Workflows argument size limit (64 KB).** Zero coverage. If /batch returns a large payload to Workflows, the workflow execution can fail to record it.
- **Healthcheck / startup probe configuration.** None of the three teams asked whether Cloud Run startup, liveness, or readiness probes are configured. Node.js + Firestore connection-init means an instance can serve before it is ready.

---

## Triple Blind Spot (consolidator's view, conservative)

**Software supply chain / image provenance / Binary Authorization.**

Two of the three teams identified an "RCE in upstream RSS parsing library" (Gemini Misuse A) or attacker-controlled-URL paths (Claude C4) as the entry vector that turns `roles/editor` into project compromise. Yet **no team asked**:

- Where does the news-fetcher container image come from?
- Who can push to `us-central1-docker.pkg.dev/PROJECT/services/news-fetcher`?
- Is Binary Authorization enabled on Cloud Run?
- Is dependency scanning (SCA) in CI?
- Is the build pipeline itself audited?

The combination already on the table is structurally ugly:

1. C10 — `:latest` is a mutable tag (rollback hazard).
2. C5 — third-party RSS parser is the assumed RCE surface.
3. C2 — `roles/editor` SA on the runtime.
4. (Unflagged) — no supply-chain controls mentioned.

`:latest` is not just a rollback footgun; it is an attacker-persistence vector. Push a malicious image once, every cold start (every hour, given `minScale: 0`) pulls it. With the SA carrying `roles/editor`, the attacker's amplification factor is the entire project.

*Conservative caveat:* the original plan may assume a separate hardened build pipeline exists out of band. Neither the plan nor any of the three teams says so. Silence on supply chain when the explicit attack model is "RCE via dependency" is a real hole — worth a human reviewer's attention.
