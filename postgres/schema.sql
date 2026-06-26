-- Utility Data Governance & Data Quality Lab
-- Normalized PostgreSQL utility source schema.
--
-- This script is intentionally rerunnable for local practice environments.

DROP SCHEMA IF EXISTS utility_curated CASCADE;
DROP SCHEMA IF EXISTS utility_source CASCADE;

CREATE SCHEMA utility_source;

CREATE TABLE utility_source.service_locations (
    service_location_id SERIAL PRIMARY KEY,
    service_location_number VARCHAR(50) NOT NULL UNIQUE,
    address_line_1 VARCHAR(255) NOT NULL,
    address_line_2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    county VARCHAR(100),
    service_type VARCHAR(50) NOT NULL,
    service_status VARCHAR(50) NOT NULL,
    latitude NUMERIC(10,6),
    longitude NUMERIC(10,6),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT chk_service_locations_type
        CHECK (service_type IN ('GAS_RESIDENTIAL', 'GAS_COMMERCIAL', 'GAS_INDUSTRIAL')),
    CONSTRAINT chk_service_locations_status
        CHECK (service_status IN ('ACTIVE', 'INACTIVE', 'PENDING', 'RETIRED'))
);

CREATE TABLE utility_source.customer_service_accounts (
    customer_service_account_id SERIAL PRIMARY KEY,
    customer_account_number VARCHAR(50) NOT NULL UNIQUE,
    service_location_id INTEGER NOT NULL,
    customer_name VARCHAR(200) NOT NULL,
    customer_type VARCHAR(50) NOT NULL,
    account_status VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    billing_cycle VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT fk_customer_service_accounts_location
        FOREIGN KEY (service_location_id)
        REFERENCES utility_source.service_locations(service_location_id),
    CONSTRAINT chk_customer_service_accounts_type
        CHECK (customer_type IN ('RESIDENTIAL', 'COMMERCIAL', 'INDUSTRIAL')),
    CONSTRAINT chk_customer_service_accounts_status
        CHECK (account_status IN ('ACTIVE', 'INACTIVE', 'CLOSED', 'PENDING')),
    CONSTRAINT chk_customer_service_accounts_dates
        CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE TABLE utility_source.hr_employees (
    employee_id SERIAL PRIMARY KEY,
    employee_number VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    job_title VARCHAR(150) NOT NULL,
    employment_status VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL,
    manager_employee_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT fk_hr_employees_manager
        FOREIGN KEY (manager_employee_id)
        REFERENCES utility_source.hr_employees(employee_id),
    CONSTRAINT chk_hr_employees_status
        CHECK (employment_status IN ('ACTIVE', 'INACTIVE', 'TERMINATED', 'LEAVE'))
);

CREATE TABLE utility_source.erp_assets (
    asset_id SERIAL PRIMARY KEY,
    asset_number VARCHAR(50) NOT NULL UNIQUE,
    asset_type VARCHAR(100) NOT NULL,
    asset_status VARCHAR(50) NOT NULL,
    install_date DATE NOT NULL,
    service_location_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT fk_erp_assets_location
        FOREIGN KEY (service_location_id)
        REFERENCES utility_source.service_locations(service_location_id),
    CONSTRAINT chk_erp_assets_type
        CHECK (asset_type IN ('SERVICE_LINE', 'REGULATOR', 'VALVE', 'MAIN', 'RISER', 'PRESSURE_SENSOR')),
    CONSTRAINT chk_erp_assets_status
        CHECK (asset_status IN ('ACTIVE', 'INACTIVE', 'RETIRED', 'MAINTENANCE'))
);

CREATE TABLE utility_source.erp_work_orders (
    work_order_id SERIAL PRIMARY KEY,
    work_order_number VARCHAR(50) NOT NULL UNIQUE,
    asset_id INTEGER NOT NULL,
    assigned_employee_id INTEGER,
    work_order_type VARCHAR(100) NOT NULL,
    priority VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    opened_date DATE NOT NULL,
    closed_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT fk_erp_work_orders_asset
        FOREIGN KEY (asset_id) REFERENCES utility_source.erp_assets(asset_id),
    CONSTRAINT fk_erp_work_orders_employee
        FOREIGN KEY (assigned_employee_id)
        REFERENCES utility_source.hr_employees(employee_id),
    CONSTRAINT chk_erp_work_orders_type
        CHECK (work_order_type IN ('INSPECTION', 'REPAIR', 'INSTALLATION', 'MAINTENANCE', 'EMERGENCY_RESPONSE')),
    CONSTRAINT chk_erp_work_orders_priority
        CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    CONSTRAINT chk_erp_work_orders_status
        CHECK (status IN ('OPEN', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
    CONSTRAINT chk_erp_work_orders_dates
        CHECK (closed_date IS NULL OR closed_date >= opened_date)
);

CREATE TABLE utility_source.ami_meters (
    meter_id SERIAL PRIMARY KEY,
    meter_number VARCHAR(50) NOT NULL UNIQUE,
    service_location_id INTEGER NOT NULL,
    meter_type VARCHAR(50) NOT NULL,
    meter_status VARCHAR(50) NOT NULL,
    install_date DATE NOT NULL,
    last_read_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT fk_ami_meters_location
        FOREIGN KEY (service_location_id)
        REFERENCES utility_source.service_locations(service_location_id),
    CONSTRAINT chk_ami_meters_type
        CHECK (meter_type IN ('AMI_GAS', 'SMART_GAS', 'LEGACY_GAS')),
    CONSTRAINT chk_ami_meters_status
        CHECK (meter_status IN ('ACTIVE', 'INACTIVE', 'RETIRED', 'PENDING'))
);

CREATE TABLE utility_source.ami_meter_readings (
    reading_id SERIAL PRIMARY KEY,
    meter_id INTEGER NOT NULL,
    reading_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    usage_quantity NUMERIC(12,3) NOT NULL,
    usage_unit VARCHAR(20) NOT NULL,
    reading_type VARCHAR(50) NOT NULL,
    read_status VARCHAR(50) NOT NULL,
    source_system VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT fk_ami_meter_readings_meter
        FOREIGN KEY (meter_id) REFERENCES utility_source.ami_meters(meter_id),
    CONSTRAINT chk_ami_meter_readings_quantity
        CHECK (usage_quantity >= 0),
    CONSTRAINT chk_ami_meter_readings_unit
        CHECK (usage_unit IN ('CCF', 'MCF', 'THERM')),
    CONSTRAINT chk_ami_meter_readings_type
        CHECK (reading_type IN ('INTERVAL', 'DAILY', 'ESTIMATED', 'MANUAL')),
    CONSTRAINT chk_ami_meter_readings_status
        CHECK (read_status IN ('VALID', 'ESTIMATED', 'MISSING', 'ERROR'))
);

CREATE INDEX idx_customer_service_accounts_service_location_id
    ON utility_source.customer_service_accounts(service_location_id);
CREATE INDEX idx_hr_employees_manager_employee_id
    ON utility_source.hr_employees(manager_employee_id);
CREATE INDEX idx_erp_assets_service_location_id
    ON utility_source.erp_assets(service_location_id);
CREATE INDEX idx_erp_work_orders_asset_id
    ON utility_source.erp_work_orders(asset_id);
CREATE INDEX idx_erp_work_orders_assigned_employee_id
    ON utility_source.erp_work_orders(assigned_employee_id);
CREATE INDEX idx_ami_meters_service_location_id
    ON utility_source.ami_meters(service_location_id);
CREATE INDEX idx_ami_meter_readings_meter_id
    ON utility_source.ami_meter_readings(meter_id);
CREATE INDEX idx_service_locations_city
    ON utility_source.service_locations(city);
CREATE INDEX idx_service_locations_service_status
    ON utility_source.service_locations(service_status);
CREATE INDEX idx_customer_service_accounts_account_status
    ON utility_source.customer_service_accounts(account_status);
CREATE INDEX idx_hr_employees_department
    ON utility_source.hr_employees(department);
CREATE INDEX idx_hr_employees_employment_status
    ON utility_source.hr_employees(employment_status);
CREATE INDEX idx_erp_assets_asset_status
    ON utility_source.erp_assets(asset_status);
CREATE INDEX idx_erp_work_orders_status
    ON utility_source.erp_work_orders(status);
CREATE INDEX idx_erp_work_orders_priority
    ON utility_source.erp_work_orders(priority);
CREATE INDEX idx_ami_meters_meter_status
    ON utility_source.ami_meters(meter_status);
CREATE INDEX idx_ami_meter_readings_reading_timestamp
    ON utility_source.ami_meter_readings(reading_timestamp);
CREATE INDEX idx_ami_meter_readings_read_status
    ON utility_source.ami_meter_readings(read_status);
