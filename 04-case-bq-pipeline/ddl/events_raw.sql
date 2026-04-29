-- events_raw.sql
-- Staging table for raw event data loaded from GCS exports.
-- Truncated daily before the next load (replace-mode load job).

CREATE TABLE IF NOT EXISTS `analytics.events_raw_staging` (
  user_id         STRING    NOT NULL,
  order_id        STRING    NOT NULL,
  event_type      STRING    NOT NULL,    -- add_to_cart | checkout | paid
  event_ts        TIMESTAMP NOT NULL,
  source_event_id STRING,
  loaded_at       TIMESTAMP             DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(event_ts);
