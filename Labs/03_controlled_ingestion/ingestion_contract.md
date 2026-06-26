# Lab 03 Ingestion Contract

## Purpose

This lab simulates controlled source-to-raw ingestion for utility data.

The goal is not only to copy data. The goal is to prove that each source table was extracted from an approved source, landed in the expected raw location, and reconciled back to the source.

## Source system

Local source database:

```text
PostgreSQL database: utility_governance_lab
Source schema: utility_source
```

Production equivalent:

```text
ERP, HR, AMI, customer, asset, work-order, and service-location systems
```

## Approved source tables

Only these tables are approved for Lab 03 ingestion:

| Table | Source system | Primary key | Control total |
|---|---|---|---|
| `service_locations` | utility_location_master | `service_location_id` | none |
| `customer_service_accounts` | customer_information_system | `customer_service_account_id` | none |
| `hr_employees` | human_resources | `employee_id` | none |
| `erp_assets` | enterprise_resource_planning | `asset_id` | none |
| `erp_work_orders` | enterprise_resource_planning | `work_order_id` | none |
| `ami_meters` | advanced_metering_infrastructure | `meter_id` | none |
| `ami_meter_readings` | advanced_metering_infrastructure | `reading_id` | `SUM(usage_quantity)` |

Table names are controlled by a whitelist in the scripts. This prevents accidental extraction of unapproved tables and avoids unsafe dynamic SQL from user-provided identifiers.

## Raw output convention

Raw data lands under:

```text
data/raw/utility_source/<table_name>/load_date=<YYYY-MM-DD>/
```

Example:

```text
data/raw/utility_source/ami_meter_readings/load_date=2026-06-25/ami_meter_readings_<run_id>.parquet
```

The load date is part of the directory path so each ingestion batch is auditable and easy to validate.

## Raw metadata columns

Each raw Parquet file includes these metadata columns:

| Metadata column | Meaning |
|---|---|
| `_source_system` | Business/source-system label |
| `_source_schema` | PostgreSQL source schema |
| `_source_table` | PostgreSQL source table |
| `_extraction_time_utc` | UTC time when the table was extracted |
| `_load_date` | Controlled batch/load date |
| `_run_id` | Unique ingestion run ID |

These columns make the raw layer traceable.

## Validation rules

The ingestion process validates:

1. `load_date` is valid `YYYY-MM-DD`.
2. Every requested table is on the approved whitelist.
3. Output for the same table and load date does not already exist.
4. Source row count equals raw Parquet row count.
5. AMI source usage total equals raw AMI usage total.
6. Raw files can be read back after writing.
7. Failures return a non-zero exit code.
8. Credentials are read from environment variables, not hard-coded in scripts.

## How to run

From the repository root:

```powershell
python Labs/03_controlled_ingestion/run_utility_ingestion.py --load-date 2026-06-25
```

Validate the landed raw data:

```powershell
python Labs/03_controlled_ingestion/validate_raw_load.py --load-date 2026-06-25
```

Run only selected tables:

```powershell
python Labs/03_controlled_ingestion/run_utility_ingestion.py --load-date 2026-06-25 --tables ami_meters,ami_meter_readings
```

```powershell
python Labs/03_controlled_ingestion/validate_raw_load.py --load-date 2026-06-25 --tables ami_meters,ami_meter_readings
```

## Expected successful row counts

| Table | Expected rows |
|---|---:|
| `service_locations` | 500 |
| `customer_service_accounts` | 650 |
| `hr_employees` | 120 |
| `erp_assets` | 800 |
| `erp_work_orders` | 600 |
| `ami_meters` | 1,000 |
| `ami_meter_readings` | 30,000 |

Expected AMI usage control total:

```text
SUM(usage_quantity) = 982691.232
```

## Enterprise takeaway

> I built a controlled source-to-raw ingestion process with approved-table whitelisting, validated load dates, schema-qualified extraction, raw Parquet output partitioned by load date, audit metadata, read-back validation, row-count reconciliation, AMI control-total reconciliation, and non-zero failure exits. This makes the raw layer traceable, reproducible, and safer for production-style data movement.
