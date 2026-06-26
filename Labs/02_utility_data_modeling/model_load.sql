-- Lab 02 — Load Curated Utility Data Model
-- Run this after model_ddl.sql.

INSERT INTO utility_curated.dim_service_location (
    service_location_key,
    service_location_id,
    service_location_number,
    address_line_1,
    address_line_2,
    city,
    state,
    postal_code,
    county,
    service_type,
    service_status,
    latitude,
    longitude,
    source_created_at,
    source_updated_at
)
SELECT
    service_location_id AS service_location_key,
    service_location_id,
    service_location_number,
    address_line_1,
    address_line_2,
    city,
    state,
    postal_code,
    county,
    service_type,
    service_status,
    latitude,
    longitude,
    created_at,
    updated_at
FROM utility_source.service_locations;

INSERT INTO utility_curated.dim_meter (
    meter_key,
    meter_id,
    meter_number,
    service_location_key,
    meter_type,
    meter_status,
    install_date,
    last_read_date,
    source_created_at,
    source_updated_at
)
SELECT
    m.meter_id AS meter_key,
    m.meter_id,
    m.meter_number,
    sl.service_location_id AS service_location_key,
    m.meter_type,
    m.meter_status,
    m.install_date,
    m.last_read_date,
    m.created_at,
    m.updated_at
FROM utility_source.ami_meters m
JOIN utility_source.service_locations sl
  ON m.service_location_id = sl.service_location_id;

INSERT INTO utility_curated.dim_asset (
    asset_key,
    asset_id,
    asset_number,
    service_location_key,
    asset_type,
    asset_status,
    install_date,
    source_created_at,
    source_updated_at
)
SELECT
    a.asset_id AS asset_key,
    a.asset_id,
    a.asset_number,
    sl.service_location_id AS service_location_key,
    a.asset_type,
    a.asset_status,
    a.install_date,
    a.created_at,
    a.updated_at
FROM utility_source.erp_assets a
JOIN utility_source.service_locations sl
  ON a.service_location_id = sl.service_location_id;

INSERT INTO utility_curated.dim_employee (
    employee_key,
    employee_id,
    employee_number,
    first_name,
    last_name,
    department,
    job_title,
    employment_status,
    hire_date,
    manager_employee_id,
    source_created_at,
    source_updated_at
)
SELECT
    employee_id AS employee_key,
    employee_id,
    employee_number,
    first_name,
    last_name,
    department,
    job_title,
    employment_status,
    hire_date,
    manager_employee_id,
    created_at,
    updated_at
FROM utility_source.hr_employees;

INSERT INTO utility_curated.fact_meter_usage_daily (
    meter_key,
    service_location_key,
    reading_date,
    readings_per_meter_day,
    daily_usage_quantity,
    usage_unit,
    estimated_read_count,
    actual_read_count
)
SELECT
    m.meter_id AS meter_key,
    m.service_location_id AS service_location_key,
    r.reading_timestamp::date AS reading_date,
    COUNT(*) AS readings_per_meter_day,
    SUM(r.usage_quantity) AS daily_usage_quantity,
    MAX(r.usage_unit) AS usage_unit,
    COUNT(*) FILTER (WHERE r.reading_type = 'ESTIMATED') AS estimated_read_count,
    COUNT(*) FILTER (WHERE r.reading_type = 'ACTUAL') AS actual_read_count
FROM utility_source.ami_meter_readings r
JOIN utility_source.ami_meters m
  ON r.meter_id = m.meter_id
GROUP BY
    m.meter_id,
    m.service_location_id,
    r.reading_timestamp::date;

INSERT INTO utility_curated.fact_work_order (
    work_order_key,
    work_order_id,
    work_order_number,
    asset_key,
    service_location_key,
    assigned_employee_key,
    work_order_type,
    priority,
    status,
    opened_date,
    closed_date,
    days_to_close,
    is_open,
    is_completed,
    is_high_priority
)
SELECT
    wo.work_order_id AS work_order_key,
    wo.work_order_id,
    wo.work_order_number,
    wo.asset_id AS asset_key,
    a.service_location_id AS service_location_key,
    wo.assigned_employee_id AS assigned_employee_key,
    wo.work_order_type,
    wo.priority,
    wo.status,
    wo.opened_date,
    wo.closed_date,
    CASE
        WHEN wo.closed_date IS NOT NULL THEN wo.closed_date - wo.opened_date
        ELSE NULL
    END AS days_to_close,
    wo.status IN ('OPEN', 'IN_PROGRESS') AS is_open,
    wo.status = 'COMPLETED' AS is_completed,
    wo.priority IN ('HIGH', 'CRITICAL') AS is_high_priority
FROM utility_source.erp_work_orders wo
JOIN utility_source.erp_assets a
  ON wo.asset_id = a.asset_id;
