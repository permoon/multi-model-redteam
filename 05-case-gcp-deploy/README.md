# Chapter 05 — Case: GCP Cloud Run deploy

> 🚧 Under construction — built on Day 5 (actual run, not synthetic).

## What you'll see

A real-world Cloud Run + Cloud Workflows deploy plan for a service called
`news-fetcher`. The plan has 7 hidden flaws: IAM `roles/editor`, region
mismatch (Cloud Run vs Workflows), `:latest` image tag, no retry on
Workflows, etc. Three LLMs surface different subsets — Gemini tends to
catch GCP-specific traps, Claude catches rollback gaps.

## Files (when complete)

- `plan.md` — design (no spoiler comments)
- `cloudrun.yaml`, `workflows.yaml`, `iam.yaml` — actual configs
- `run-redteam.sh`
- `expected-findings.md` — Day 5 actual output

[← Back to README](../README.md)
