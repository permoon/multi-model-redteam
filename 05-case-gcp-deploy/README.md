# Chapter 05 — Case: GCP Cloud Run deploy

A real-world Cloud Run + Cloud Workflows deploy plan for a service called
`news-fetcher` (Node.js Express app, hourly batch fan-out + ad-hoc
requests). The plan is written the way an engineer might propose a GKE
→ Cloud Run migration on day one — looks reasonable, but has 7 hidden
flaws spanning IAM, region, reliability, and reproducibility.

## Files

- [`plan.md`](./plan.md) — the design under review (no spoiler comments)
- [`cloudrun.yaml`](./cloudrun.yaml) — Cloud Run service config
- [`workflows.yaml`](./workflows.yaml) — Cloud Workflows orchestration
- [`iam.yaml`](./iam.yaml) — IAM bindings
- [`run-redteam.sh`](./run-redteam.sh) — runs the red team, outputs to a timestamped dir
- `expected-findings.md` — actual findings from a Day 5 canonical run, with metadata header (created after first real run)

## How to run

```bash
cd 05-case-gcp-deploy
bash run-redteam.sh
# → ./out-<timestamp>/ranked.md
```

Cost: ~$0.30 per run (3 model calls + consolidate + rank).

## What this case demonstrates

This plan looks like reasonable engineer output: yaml is structured,
IAM is scoped to two service accounts, regions are listed, monitoring
is mentioned, the migration plan has a fallback. A single LLM review
will catch some issues but miss others. Run the red team and compare
consensus findings (≥ 2 teams) against unique findings (1 team) — the
latter are where the value compounds.

Specifically, this case is designed to surface:

- An **IAM scope decision**: `roles/editor` granted to `news-fetcher-sa`
  is far broader than the actual needs (Firestore read + Pub/Sub publish)
- A **region locality issue**: Cloud Run is `us-central1`, Workflows is
  `us-east1` — every hourly invocation pays cross-region latency and
  egress
- An **environment hardcoding**: `FIRESTORE_PROJECT=my-prod-project`
  inside `cloudrun.yaml` means staging deploys hit prod Firestore
- A **reliability gap**: Workflows has no retry policy, so a single
  transient HTTP failure (or Cloud Run cold start exceeding the OIDC
  call timeout) drops one hour of news ingestion
- A **latency SLO conflict**: `minScale: 0` plus a 95% < 500ms target
  is incompatible — Cloud Run cold starts on Node.js typically exceed
  500ms after idle scale-down
- A **rollback strategy gap**: no mention of revision pinning, traffic
  splits, or a procedure to revert a bad deploy
- A **reproducibility issue**: `:latest` image tag means re-deploys can
  pick up different binaries; no way to roll forward to "the version
  that was running yesterday"

The point is **not** that this plan is bad — it's that even a sensible
plan has 7 invisible-to-one-LLM flaws. Multi-model surfaces them.
Different models tend to specialize: Gemini catches GCP-native
patterns (region, IAM), Claude catches operational gaps (retry,
rollback), Codex catches generic anti-patterns (`:latest`, hardcoded
config) — and the consensus + unique split reveals the blind spots.

## When you've run it

The first time you run `run-redteam.sh`, an `out-<timestamp>/` directory
appears. Pick the run you trust most, then:

1. `cp out-<timestamp>/consolidated.md expected-findings.md`
2. Prepend the metadata header from
   [`../examples/expected-findings-template.md`](../examples/expected-findings-template.md)
   (run date, model versions, CLI versions)
3. Commit `expected-findings.md` so future readers can compare

The `out-<timestamp>/` directory itself is gitignored (per the root
`.gitignore`) — only the curated `expected-findings.md` is tracked.

[← Back to README](../README.md) · [中文版](./README.zh-TW.md)
