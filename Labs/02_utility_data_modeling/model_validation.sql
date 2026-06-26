-- Lab 02 — Curated Model Validation
-- Run this after model_ddl.sql and model_load.sql.

-- 1. Curated row counts
SELECT 'dim_service_location' AS table_name, COUNT(*) AS row_count
FROM utility_curated.dim_service_location
UNION ALL
SELECT 'dim_meter', COUNT(*)
FROM utility_curated.dim_meter
UNION ALL
SELECT 'dim_asset', COUNT(*)
FROM utility_curated.dim_asset
UNION ALL
SELECT 'dim_employee', COUNT(*)
FROM utility_curated.dim_employee
UNION ALL
SELECT 'fact_meter_usage_daily', COUNT(*)
FROM utility_curated.fact_meter_usage_daily
UNION ALL
SELECT 'fact_work_order', COUNT(*)
FROM utility_curated.fact_work_order
ORDER BY table_name;

-- 2. Validate dimension business-key uniqueness
SELECT 'dim_service_location.service_location_number' AS check_name,
       COUNT(*) - COUNT(DISTINCT service_location_number) AS duplicate_count
FROM utility_curated.dim_service_location
UNION ALL
SELECT 'dim_meter.meter_number',
       COUNT(*) - COUNT(DISTINCT meter_number)
FROM utility_curated.dim_meter
UNION ALL
SELECT 'dim_asset.asset_number',
       COUNT(*) - COUNT(DISTINCT asset_number)
FROM utility_curated.dim_asset
UNION ALL
SELECT 'dim_employee.employee_number',
       COUNT(*) - COUNT(DISTINCT employee_number)
FROM utility_curated.dim_employee;

-- 3. Validate fact_meter_usage_daily grain: one row per meter per reading date
SELECT
    meter_key,
    reading_date,
    COUNT(*) AS rows_at_grain
FROM utility_curated.fact_meter_usage_daily
GROUP BY
    meter_key,
    reading_date
HAVING COUNT(*) > 1;

-- 4. Validate fact_work_order grain: one row per work order
SELECT
    work_order_id,
    COUNT(*) AS rows_at_grain
FROM utility_curated.fact_work_order
GROUP BY work_order_id
HAVING COUNT(*) > 1;

-- 5. Reconcile source AMI usage to curated daily fact
SELECT
    source_usage.total_source_usage,
    curated_usage.total_curated_usage,
    source_usage.total_source_usage - curated_usage.total_curated_usage AS usage_difference
FROM (
    SELECT SUM(usage_quantity) AS total_source_usage
    FROM utility_source.ami_meter_readings
) source_usage
CROSS JOIN (
    SELECT SUM(daily_usage_quantity) AS total_curated_usage
    FROM utility_curated.fact_meter_usage_daily
) curated_usage;

-- 6. Reconcile source work-order count to curated fact count
SELECT
    source_count.source_work_orders,
    curated_count.curated_work_orders,
    source_count.source_work_orders - curated_count.curated_work_orders AS count_difference
FROM (
    SELECT COUNT(*) AS source_work_orders
    FROM utility_source.erp_work_orders
) source_count
CROSS JOIN (
    SELECT COUNT(*) AS curated_work_orders
    FROM utility_curated.fact_work_order
) curated_count;

-- 7. Confirm all curated work orders have asset and location context
SELECT
    COUNT(*) AS work_orders_missing_required_dimension_context
FROM utility_curated.fact_work_order wo
LEFT JOIN utility_curated.dim_asset a
  ON wo.asset_key = a.asset_key
LEFT JOIN utility_curated.dim_service_location sl
  ON wo.service_location_key = sl.service_location_key
WHERE a.asset_key IS NULL
   OR sl.service_location_key IS NULL;

-- 8. Example reporting query: daily usage by city
SELECT
    f.reading_date,
    sl.city,
    COUNT(DISTINCT f.meter_key) AS meter_count,
    SUM(f.daily_usage_quantity) AS total_daily_usage
FROM utility_curated.fact_meter_usage_daily f
JOIN utility_curated.dim_service_location sl
  ON f.service_location_key = sl.service_location_key
GROUP BY
    f.reading_date,
    sl.city
ORDER BY
    f.reading_date,
    sl.city
LIMIT 100;

-- 9. Example reporting query: work-order volume by priority and status
SELECT
    priority,
    status,
    COUNT(*) AS work_order_count,
    AVG(days_to_close) AS avg_days_to_close
FROM utility_curated.fact_work_order
GROUP BY
    priority,
    status
ORDER BY
    priority,
    status;
