-- Lab 02 — Curated Utility Data Model DDL
-- Run this script in PostgreSQL.
-- It creates a curated reporting schema from the utility source tables.

CREATE SCHEMA IF NOT EXISTS utility_curated;

DROP TABLE IF EXISTS utility_curated.fact_work_order;
DROP TABLE IF EXISTS utility_curated.fact_meter_usage_daily;
DROP TABLE IF EXISTS utility_curated.dim_employee;
DROP TABLE IF EXISTS utility_curated.dim_asset;
DROP TABLE IF EXISTS utility_curated.dim_meter;
DROP TABLE IF EXISTS utility_curated.dim_service_location;

CREATE TABLE utility_curated.dim_service_location (
    service_location_key       INTEGER PRIMARY KEY,
    service_location_id        INTEGER NOT NULL UNIQUE,
    service_location_number    VARCHAR(30) NOT NULL UNIQUE,
    address_line_1             VARCHAR(200) NOT NULL,
    address_line_2             VARCHAR(200),
    city                       VARCHAR(100) NOT NULL,
    state                      VARCHAR(2) NOT NULL,
    postal_code                VARCHAR(20) NOT NULL,
    county                     VARCHAR(100),
    service_type               VARCHAR(50) NOT NULL,
    service_status             VARCHAR(30) NOT NULL,
    latitude                   NUMERIC(9, 6),
    longitude                  NUMERIC(9, 6),
    source_created_at          TIMESTAMPTZ,
    source_updated_at          TIMESTAMPTZ,
    curated_loaded_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE utility_curated.dim_meter (
    meter_key                  INTEGER PRIMARY KEY,
    meter_id                   INTEGER NOT NULL UNIQUE,
    meter_number               VARCHAR(30) NOT NULL UNIQUE,
    service_location_key       INTEGER NOT NULL REFERENCES utility_curated.dim_service_location(service_location_key),
    meter_type                 VARCHAR(50) NOT NULL,
    meter_status               VARCHAR(30) NOT NULL,
    install_date               DATE NOT NULL,
    last_read_date             DATE,
    source_created_at          TIMESTAMPTZ,
    source_updated_at          TIMESTAMPTZ,
    curated_loaded_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE utility_curated.dim_asset (
    asset_key                  INTEGER PRIMARY KEY,
    asset_id                   INTEGER NOT NULL UNIQUE,
    asset_number               VARCHAR(30) NOT NULL UNIQUE,
    service_location_key       INTEGER NOT NULL REFERENCES utility_curated.dim_service_location(service_location_key),
    asset_type                 VARCHAR(50) NOT NULL,
    asset_status               VARCHAR(30) NOT NULL,
    install_date               DATE NOT NULL,
    source_created_at          TIMESTAMPTZ,
    source_updated_at          TIMESTAMPTZ,
    curated_loaded_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE utility_curated.dim_employee (
    employee_key               INTEGER PRIMARY KEY,
    employee_id                INTEGER NOT NULL UNIQUE,
    employee_number            VARCHAR(30) NOT NULL UNIQUE,
    first_name                 VARCHAR(100) NOT NULL,
    last_name                  VARCHAR(100) NOT NULL,
    department                 VARCHAR(100) NOT NULL,
    job_title                  VARCHAR(100) NOT NULL,
    employment_status          VARCHAR(30) NOT NULL,
    hire_date                  DATE NOT NULL,
    manager_employee_id        INTEGER,
    source_created_at          TIMESTAMPTZ,
    source_updated_at          TIMESTAMPTZ,
    curated_loaded_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE utility_curated.fact_meter_usage_daily (
    meter_key                  INTEGER NOT NULL REFERENCES utility_curated.dim_meter(meter_key),
    service_location_key       INTEGER NOT NULL REFERENCES utility_curated.dim_service_location(service_location_key),
    reading_date               DATE NOT NULL,
    readings_per_meter_day     INTEGER NOT NULL,
    daily_usage_quantity       NUMERIC(18, 3) NOT NULL,
    usage_unit                 VARCHAR(20) NOT NULL,
    estimated_read_count       INTEGER NOT NULL,
    actual_read_count          INTEGER NOT NULL,
    curated_loaded_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (meter_key, reading_date)
);

CREATE TABLE utility_curated.fact_work_order (
    work_order_key             INTEGER PRIMARY KEY,
    work_order_id              INTEGER NOT NULL UNIQUE,
    work_order_number          VARCHAR(30) NOT NULL UNIQUE,
    asset_key                  INTEGER NOT NULL REFERENCES utility_curated.dim_asset(asset_key),
    service_location_key       INTEGER NOT NULL REFERENCES utility_curated.dim_service_location(service_location_key),
    assigned_employee_key      INTEGER REFERENCES utility_curated.dim_employee(employee_key),
    work_order_type            VARCHAR(50) NOT NULL,
    priority                   VARCHAR(30) NOT NULL,
    status                     VARCHAR(30) NOT NULL,
    opened_date                DATE NOT NULL,
    closed_date                DATE,
    days_to_close              INTEGER,
    is_open                    BOOLEAN NOT NULL,
    is_completed               BOOLEAN NOT NULL,
    is_high_priority           BOOLEAN NOT NULL,
    curated_loaded_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fact_meter_usage_daily_reading_date
    ON utility_curated.fact_meter_usage_daily(reading_date);

CREATE INDEX idx_fact_meter_usage_daily_location
    ON utility_curated.fact_meter_usage_daily(service_location_key);

CREATE INDEX idx_fact_work_order_location
    ON utility_curated.fact_work_order(service_location_key);

CREATE INDEX idx_fact_work_order_asset
    ON utility_curated.fact_work_order(asset_key);

CREATE INDEX idx_fact_work_order_employee
    ON utility_curated.fact_work_order(assigned_employee_key);

CREATE INDEX idx_fact_work_order_opened_date
    ON utility_curated.fact_work_order(opened_date);
