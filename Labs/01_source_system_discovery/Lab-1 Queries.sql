SELECT current_database(), current_user, current_schema();

-- List utility source tables
SELECT table_schema, table_name, table_type FROM information_schema.tables 
WHERE table_schema = 'utility_source'
ORDER BY table_name;

-- Inventory utility source columns
SELECT
    table_name,
    ordinal_position,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'utility_source'
ORDER BY table_name, ordinal_position;

-- Reconcile source row counts
SELECT 'service_locations' AS table_name, COUNT(*) AS row_count
FROM utility_source.service_locations

UNION ALL

SELECT 'customer_service_accounts', COUNT(*)
FROM utility_source.customer_service_accounts

UNION ALL

SELECT 'hr_employees', COUNT(*)
FROM utility_source.hr_employees

UNION ALL

SELECT 'erp_assets', COUNT(*)
FROM utility_source.erp_assets

UNION ALL

SELECT 'erp_work_orders', COUNT(*)
FROM utility_source.erp_work_orders

UNION ALL

SELECT 'ami_meters', COUNT(*)
FROM utility_source.ami_meters

UNION ALL

SELECT 'ami_meter_readings', COUNT(*)
FROM utility_source.ami_meter_readings

ORDER BY table_name;

-- Profile AMI event history
SELECT
    MIN(reading_timestamp) AS earliest_reading,
    MAX(reading_timestamp) AS latest_reading,
    COUNT(DISTINCT reading_timestamp::date) AS reading_days
FROM utility_source.ami_meter_readings;
