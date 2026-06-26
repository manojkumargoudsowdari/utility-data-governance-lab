-- Lab 02 — Utility Data Modeling
-- Run these queries one section at a time.
-- Assumption: your PostgreSQL connection search_path is set to utility_source, public.

-- 1. Confirm current database/schema context
SELECT
    current_database() AS current_database,
    current_user AS current_user,
    current_schema() AS current_schema;

-- 2. List source tables
SELECT
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'utility_source'
ORDER BY table_name;

-- 3. Discover primary keys and unique constraints
SELECT
    tc.table_name,
    tc.constraint_type,
    tc.constraint_name,
    kcu.column_name,
    kcu.ordinal_position
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_schema = kcu.constraint_schema
 AND tc.constraint_name = kcu.constraint_name
WHERE tc.table_schema = 'utility_source'
  AND tc.constraint_type IN ('PRIMARY KEY', 'UNIQUE')
ORDER BY
    tc.table_name,
    tc.constraint_type,
    tc.constraint_name,
    kcu.ordinal_position;

-- 4. Discover foreign-key relationships
SELECT
    tc.table_name AS child_table,
    kcu.column_name AS child_column,
    ccu.table_name AS parent_table,
    ccu.column_name AS parent_column,
    tc.constraint_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_schema = kcu.constraint_schema
 AND tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu
  ON ccu.constraint_schema = tc.constraint_schema
 AND ccu.constraint_name = tc.constraint_name
WHERE tc.table_schema = 'utility_source'
  AND tc.constraint_type = 'FOREIGN KEY'
ORDER BY
    child_table,
    child_column;

-- 5. Inspect likely business keys
SELECT
    'service_locations' AS table_name,
    COUNT(*) AS row_count,
    COUNT(DISTINCT service_location_id) AS distinct_primary_key,
    COUNT(DISTINCT service_location_number) AS distinct_business_key
FROM service_locations
UNION ALL
SELECT
    'customer_service_accounts',
    COUNT(*),
    COUNT(DISTINCT customer_service_account_id),
    COUNT(DISTINCT customer_account_number)
FROM customer_service_accounts
UNION ALL
SELECT
    'hr_employees',
    COUNT(*),
    COUNT(DISTINCT employee_id),
    COUNT(DISTINCT employee_number)
FROM hr_employees
UNION ALL
SELECT
    'erp_assets',
    COUNT(*),
    COUNT(DISTINCT asset_id),
    COUNT(DISTINCT asset_number)
FROM erp_assets
UNION ALL
SELECT
    'erp_work_orders',
    COUNT(*),
    COUNT(DISTINCT work_order_id),
    COUNT(DISTINCT work_order_number)
FROM erp_work_orders
UNION ALL
SELECT
    'ami_meters',
    COUNT(*),
    COUNT(DISTINCT meter_id),
    COUNT(DISTINCT meter_number)
FROM ami_meters;

-- 6. Check AMI reading grain: one meter per reading timestamp
SELECT
    meter_id,
    reading_timestamp,
    COUNT(*) AS records_at_grain
FROM ami_meter_readings
GROUP BY
    meter_id,
    reading_timestamp
HAVING COUNT(*) > 1
ORDER BY records_at_grain DESC;

-- 7. Check daily AMI fact grain candidate: one meter per reading date
SELECT
    meter_id,
    reading_timestamp::date AS reading_date,
    COUNT(*) AS readings_per_meter_day,
    SUM(usage_quantity) AS daily_usage_quantity
FROM ami_meter_readings
GROUP BY
    meter_id,
    reading_timestamp::date
ORDER BY
    meter_id,
    reading_date
LIMIT 100;

-- 8. Source-to-target thinking: enrich work orders with asset, location, and employee context
SELECT
    wo.work_order_id,
    wo.work_order_number,
    wo.work_order_type,
    wo.priority,
    wo.status,
    wo.opened_date,
    wo.closed_date,
    a.asset_number,
    a.asset_type,
    sl.service_location_number,
    sl.city,
    e.employee_number,
    e.department,
    e.job_title
FROM erp_work_orders wo
JOIN erp_assets a
  ON wo.asset_id = a.asset_id
JOIN service_locations sl
  ON a.service_location_id = sl.service_location_id
LEFT JOIN hr_employees e
  ON wo.assigned_employee_id = e.employee_id
ORDER BY wo.work_order_id
LIMIT 100;
