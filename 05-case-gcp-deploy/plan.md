# Plan: news-fetcher migration to Cloud Run + Workflows

## Background

`news-fetcher` is a Node.js Express app that pulls articles from upstream
RSS feeds, normalizes them, writes to Firestore, and publishes a
notification on a Pub/Sub topic. It currently runs on GKE in a shared
`internal-svcs` cluster.

The infra team is sunsetting the shared cluster (Q3 cost reduction). We
need to move `news-fetcher` to Cloud Run + Cloud Workflows, which
simplifies operations (no node management) and matches our usage pattern
(spiky, 1× per hour batch trigger plus occasional ad-hoc requests).

Current load profile:

- Peak QPS: 200 (during the hourly batch fan-out)
- Off-peak QPS: < 5
- 95th-percentile latency target: < 500ms (downstream consumers
  timeout at 1s)
- Reads ~50 documents from Firestore per request
- Publishes one Pub/Sub message per processed article

## Goals

1. Migrate `news-fetcher` off GKE before the cluster sunset (target:
   end of next sprint)
2. Preserve the current 95% < 500ms latency SLO
3. Cut infra cost ≥ 40% by going scale-to-zero (no idle nodes)
4. Replace the current GKE CronJob with Cloud Workflows for the
   hourly batch trigger

## Cloud Run config

```yaml
# cloudrun.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: news-fetcher
  namespace: default
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "100"
    spec:
      serviceAccountName: news-fetcher-sa@PROJECT.iam.gserviceaccount.com
      containerConcurrency: 80
      containers:
      - image: us-central1-docker.pkg.dev/PROJECT/services/news-fetcher:latest
        env:
        - name: FIRESTORE_PROJECT
          value: "my-prod-project"
        - name: PUBSUB_TOPIC
          value: "news-events"
        ports:
        - containerPort: 8080
        resources:
          limits:
            cpu: "2"
            memory: "1Gi"
```

## Workflows orchestration

The hourly batch fan-out moves from a GKE CronJob to Cloud Workflows. A
single workflow calls the `/batch` endpoint on Cloud Run, which fans out
internally:

```yaml
# workflows.yaml
main:
  steps:
    - call_batch:
        call: http.post
        args:
          url: https://news-fetcher-xxxxx-uc.a.run.app/batch
          auth:
            type: OIDC
        result: response
    - log_result:
        call: sys.log
        args:
          text: ${response.body}
```

Cloud Scheduler triggers the workflow at the top of every hour
(`0 * * * *`).

## IAM

```yaml
# iam.yaml
- member: "serviceAccount:news-fetcher-sa@PROJECT.iam.gserviceaccount.com"
  role: "roles/editor"
- member: "serviceAccount:workflows-sa@PROJECT.iam.gserviceaccount.com"
  role: "roles/run.invoker"
```

## Regions

| Component         | Region              |
|-------------------|---------------------|
| Cloud Run         | us-central1         |
| Workflows         | us-east1            |
| Firestore         | nam5 (multi-region) |
| Artifact Registry | us-central1         |
| Pub/Sub topic     | global              |

## Monitoring

- Cloud Run built-in metrics: request latency, request count, error
  rate (visible in Cloud Console)
- Workflows execution failures → email `platform-oncall@valuex.example`
- Pub/Sub topic backlog alarm: existing, unchanged

## Rollout

- Deploy to the `staging` project this week using the same yaml files
  (project ID swapped via templating)
- Cut production traffic at the load-balancer level next Tuesday morning
- Keep the GKE workload warm for one week as a fallback

## Out of scope

- Migration of downstream consumers (they already consume Pub/Sub —
  no change required)
- VPC-SC private connectivity (separate ticket)
- Multi-region failover (single-region service today)
