# Chapter 05 — Case: GCP Cloud Run deploy

A real-world Cloud Run + Cloud Workflows deploy plan for a service
called `news-fetcher` (a Node.js Express app that pulls articles
from RSS feeds, hourly batch fan-out plus occasional ad-hoc
requests). It's written the way an engineer might propose a GKE-to-
Cloud-Run migration on day one — sensible-looking, with config
yamls, IAM, regions all laid out. It also has 7 hidden flaws across
IAM, region, reliability, and reproducibility.

## Files

- [`plan.md`](./plan.md) — the design under review (no spoiler
  comments)
- [`cloudrun.yaml`](./cloudrun.yaml) — Cloud Run service config
- [`workflows.yaml`](./workflows.yaml) — Cloud Workflows orchestration
- [`iam.yaml`](./iam.yaml) — IAM bindings
- [`run-redteam.sh`](./run-redteam.sh) — runs the red team and
  writes to a timestamped output directory
- `expected-findings.md` — actual findings from the Day 5 canonical
  run, with metadata header

## How to run

```bash
cd 05-case-gcp-deploy
bash run-redteam.sh
# → ./out-<timestamp>/ranked.md
```

Cost: about $0.30 per run (3 model calls, plus consolidation and
ranking).

## What this case demonstrates

This plan looks reasonable on the surface: yaml is structured, IAM
is scoped to two service accounts, regions are listed, monitoring is
mentioned, the migration plan even includes a fallback. A single-LLM
review will catch some issues but miss others. Run the red team,
then compare the consensus findings (≥ 2 teams agreed) against the
unique findings (only 1 team caught it). The unique findings are
where the value compounds.

The 7 deliberately seeded flaws, in plain English:

- **An IAM scope decision.** The service account `news-fetcher-sa`
  is bound to `roles/editor` — a project-wide role. The actual
  needs are tiny (read Firestore, publish Pub/Sub). If the service
  is compromised, `roles/editor` lets the attacker delete the
  Firestore database, push to Artifact Registry, and modify
  Pub/Sub. It should be specific roles only.
- **A region locality issue.** Cloud Run is in `us-central1`,
  Workflows is in `us-east1`. Every hourly invocation pays
  cross-region latency and cross-region egress costs. Either
  someone didn't notice, or someone assumed Workflows just picks a
  region (it doesn't).
- **An environment hardcoding.** The `cloudrun.yaml` has
  `FIRESTORE_PROJECT=my-prod-project` baked in. Deploy this same
  yaml to staging and your "staging" service starts writing to the
  prod Firestore. PII / billing risk.
- **A reliability gap.** The Workflows file has a single
  `http.post` step with no `retry` block. So one transient HTTP
  failure (or a Cloud Run cold start that takes longer than the
  workflow's default HTTP timeout) loses an entire hour of news
  ingestion.
- **A latency SLO conflict.** `minScale: 0` plus a 95% < 500ms
  latency target are mutually exclusive. After idle scale-down,
  Cloud Run cold starts on Node.js typically take 2–5 seconds. So
  the first request of every hourly batch will blow the SLO.
- **A rollback strategy gap.** Nothing in the plan mentions
  revision pinning, traffic splits, or a procedure for reverting
  a bad deploy. The "fallback" listed is "keep the old GKE
  workload warm" — but with no traffic-routing plan, you can't
  actually fail over.
- **A reproducibility issue.** The image is `:latest`. Re-deploys
  pick up whatever happens to be tagged latest at that moment,
  not what you actually validated. There's no way to roll forward
  to "the version that was running yesterday."

The point isn't that this plan is *bad* — it's that even a sensible
plan has 7 problems a single-LLM review would miss. Multi-model
surfaces them.

Different models have different specialties on this kind of thing.
Gemini tends to catch GCP-native patterns (region, IAM, service
behaviour). Claude tends to catch operational gaps (retry,
rollback, monitoring thresholds). Codex tends to catch generic
anti-patterns (`:latest`, hardcoded config). The consensus + unique
split shows you the blind spots and where each model brings
something the others didn't.

## After your first run

The first time you run `run-redteam.sh`, an `out-<timestamp>/`
directory is created. Pick the run you trust most, then:

1. `cp out-<timestamp>/consolidated.md expected-findings.md`
2. Add the metadata header from
   [`../examples/expected-findings-template.md`](../examples/expected-findings-template.md)
   (run date, model versions, CLI versions)
3. Commit `expected-findings.md` so future readers can compare

The `out-<timestamp>/` directory itself is gitignored (per the root
`.gitignore`). Only the curated `expected-findings.md` is tracked.

[← Back to README](../README.md) · [中文版](./README.zh-TW.md)
