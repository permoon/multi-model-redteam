-- events_dedup.sql
-- Final deduplicated table consumed by BI dashboards.
-- Imputed events are flagged via is_imputed.

CREATE TABLE IF NOT EXISTS `analytics.order_events_dedup` (
  user_id         STRING    NOT NULL,
  order_id        STRING    NOT NULL,
  event_type      STRING    NOT NULL,    -- add_to_cart | checkout | paid
  event_ts        TIMESTAMP NOT NULL,
  source_event_id STRING,
  is_imputed      BOOL      NOT NULL    DEFAULT FALSE
)
PARTITION BY DATE(event_ts)
CLUSTER BY user_id;
