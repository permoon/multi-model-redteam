# Plan: Order events PostgreSQL → BigQuery dedup + checkout imputation

## Background

The platform team has an `order_events` table in PostgreSQL recording user
purchase journey events: `add_to_cart`, `checkout`, `paid`. About 50M
rows total, 300k new rows per day. We want to move it to BigQuery for BI
and Looker consumption.

The mobile app has had intermittent retry bugs for ~6 months: the same
event is sometimes written 2–5 times within a few seconds. We need to
dedup as part of the migration.

A separate analytics ask: when an order has `add_to_cart` and `paid` but
no `checkout` (because the checkout event was dropped client-side), we
want to impute a synthetic `checkout` so funnel reports don't show
artificial drop-off.

## Goals

1. Daily, move yesterday's new PostgreSQL rows into BigQuery
2. Dedup by `(user_id, order_id, event_type)`, keeping the earliest
   `event_ts`
3. Impute missing `checkout` events for orders that have both
   `add_to_cart` and `paid`
4. BI dashboards consume the dedup'd table starting Monday morning

## Schema (BigQuery)

Staging table (truncated daily before each load):

```sql
CREATE TABLE `analytics.events_raw_staging` (
  user_id         STRING NOT NULL,
  order_id        STRING NOT NULL,
  event_type      STRING NOT NULL,    -- add_to_cart | checkout | paid
  event_ts        TIMESTAMP NOT NULL,
  source_event_id STRING,
  loaded_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(event_ts);
```

Final dedup'd table:

```sql
CREATE TABLE `analytics.order_events_dedup` (
  user_id         STRING NOT NULL,
  order_id        STRING NOT NULL,
  event_type      STRING NOT NULL,
  event_ts        TIMESTAMP NOT NULL,
  source_event_id STRING,
  is_imputed      BOOL NOT NULL DEFAULT FALSE
)
PARTITION BY DATE(event_ts)
CLUSTER BY user_id;
```

## Pipeline

Cloud Workflows triggered daily at 02:00 UTC:

1. **Step A** — Export yesterday's `order_events` rows from PostgreSQL to
   GCS as CSV. Filter: `WHERE event_ts >= '<yesterday>' AND event_ts < '<today>'`.
2. **Step B** — BigQuery load job from GCS into `events_raw_staging`
   (replace mode).
3. **Step C** — Dedup SQL writes into `order_events_dedup`:

   ```sql
   INSERT INTO `analytics.order_events_dedup`
   SELECT
     user_id,
     order_id,
     event_type,
     MIN(event_ts) AS event_ts,
     ANY_VALUE(source_event_id) AS source_event_id,
     FALSE AS is_imputed
   FROM `analytics.events_raw_staging`
   WHERE DATE(event_ts) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
   GROUP BY user_id, order_id, event_type;
   ```

4. **Step D** — Imputation SQL appends synthetic `checkout` rows:

   ```sql
   INSERT INTO `analytics.order_events_dedup`
   SELECT
     user_id,
     order_id,
     'checkout' AS event_type,
     TIMESTAMP_ADD(MIN(event_ts), INTERVAL 1 SECOND) AS event_ts,
     NULL AS source_event_id,
     TRUE AS is_imputed
   FROM `analytics.order_events_dedup`
   WHERE event_type IN ('add_to_cart', 'paid')
   GROUP BY user_id, order_id
   HAVING COUNT(DISTINCT event_type) = 2
      AND NOT EXISTS (
        SELECT 1 FROM `analytics.order_events_dedup` m2
        WHERE m2.user_id = user_id
          AND m2.order_id = order_id
          AND m2.event_type = 'checkout'
      );
   ```

## Monitoring

- Cloud Workflows failure → email `data-platform@valuex.example`
- BigQuery scheduled query checks daily row count: alert if the day's
  row count is **less than 50% of expected**.

## Rollout

- Staging environment: this Friday
- Production: next Monday
- BI dashboards switch to `order_events_dedup` Monday morning, after the
  first daily run completes

## Out of scope

- Real-time ingestion (this PR is daily batch only)
- Backfill of historical 6 months — separate ticket
- PII handling beyond the existing PostgreSQL setup
