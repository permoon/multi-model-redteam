-- pipeline.sql
-- Step C (dedup) and Step D (checkout imputation) of the daily pipeline.
-- See plan.md for the full design context.

-- Step C: dedup yesterday's staged events into the dedup table.
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

-- Step D: impute a synthetic 'checkout' for orders that have
-- add_to_cart + paid but no checkout.
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
