# Lab 03 Observations

## Objective

Lab 03 implemented controlled source-to-raw ingestion for the utility source system.

The goal was to extract approved PostgreSQL source tables from `utility_source` into raw Parquet files while preserving traceability, validating row counts, and detecting unsafe failure conditions.

## Successful ingestion run

Load date:

```text
2026-06-26
```

Final successful run ID:

```text
c94d3a61-b533-45e4-ae63-baa638230ead
```

Overall status:

```text
SUCCESS
```

Raw files were written under:

```text
data/raw/utility_source/<table_name>/load_date=2026-06-26/
```

## Source-to-raw reconciliation

| Source table | Source rows | Raw rows | Status |
|---|---:|---:|---|
| `service_locations` | 500 | 500 | SUCCESS |
| `customer_service_accounts` | 650 | 650 | SUCCESS |
| `hr_employees` | 120 | 120 | SUCCESS |
| `erp_assets` | 800 | 800 | SUCCESS |
| `erp_work_orders` | 600 | 600 | SUCCESS |
| `ami_meters` | 1,000 | 1,000 | SUCCESS |
| `ami_meter_readings` | 30,000 | 30,000 | SUCCESS |

The source and raw row counts matched for all seven approved source tables.

## AMI control-total reconciliation

| Control total | Value |
|---|---:|
| Source `SUM(usage_quantity)` | 982,691.232 |
| Raw `SUM(usage_quantity)` | 982,691.2320000001 |

The raw value has a tiny floating-point display difference caused by Python/Pandas numeric handling. The ingestion and validation scripts normalize control totals to the source column scale before comparison.

Result:

```text
AMI usage control total reconciled successfully.
```

## Raw metadata validation

The independent validation script confirmed that raw files were readable and included required metadata columns:

- `_source_system`
- `_source_schema`
- `_source_table`
- `_extraction_time_utc`
- `_load_date`
- `_run_id`

It also confirmed:

- `_load_date` matched `2026-06-26`
- `_source_table` matched the expected table
- raw row counts matched source row counts
- AMI usage control total reconciled

## Deliberate failure tests

### 1. Unapproved table

Command:

```powershell
python Labs/03_controlled_ingestion/run_utility_ingestion.py --load-date 2026-06-27 --tables customers
```

Result:

```text
CONFIGURATION_FAILED: Unapproved table(s): customers.
```

Purpose:

> The ingestion process only allows approved utility source tables. This prevents arbitrary or unsupported table extraction.

### 2. Invalid load date

Command:

```powershell
python Labs/03_controlled_ingestion/run_utility_ingestion.py --load-date 06-27-2026
```

Result:

```text
CONFIGURATION_FAILED: --load-date must be a valid date in YYYY-MM-DD format.
```

Purpose:

> Load-date partitions must use a consistent format so downstream processing, validation, and audit logic can depend on stable paths.

### 3. Existing load-date output

Command:

```powershell
python Labs/03_controlled_ingestion/run_utility_ingestion.py --load-date 2026-06-26
```

Result:

```text
CONFIGURATION_FAILED: Existing load-date output found. Refusing to overwrite raw data.
```

Purpose:

> Raw data should not be silently overwritten. Reruns should be explicit so the raw zone remains auditable.

### 4. Database unavailable

Commands:

```powershell
docker compose stop postgres
python Labs/03_controlled_ingestion/run_utility_ingestion.py --load-date 2026-06-29 --tables service_locations
docker compose start postgres
```

Result:

```text
status: FAILED
error: connection refused
```

Purpose:

> The pipeline fails clearly when the source database is unavailable and records the connection failure in the run summary.

### 5. Corrupt raw file

Commands:

```powershell
$amiFile = Get-ChildItem data/raw/utility_source/ami_meters/load_date=2026-06-26/*.parquet | Select-Object -First 1
Set-Content -Path $amiFile.FullName -Value "not a parquet file"
python Labs/03_controlled_ingestion/validate_raw_load.py --load-date 2026-06-26 --tables ami_meters
```

Result:

```text
status: FAILED
Parquet magic bytes not found in footer.
```

Purpose:

> Raw validation confirms that files are readable and usable, not merely present on disk.

The raw data was then restored by deleting `data/raw/utility_source` and rerunning the successful ingestion for `2026-06-26`.

## Production-style issue discovered

The first full ingestion run exposed a numeric precision issue:

```text
source=982691.232
raw=982691.2320000001
```

The pipeline initially treated this as a mismatch because it compared floating-point values directly.

Resolution:

> Control-total comparison was changed to use decimal normalization at three decimal places, matching the source `usage_quantity` scale.

This is a realistic data engineering issue because control totals often move through different engines and file formats, and numeric comparison rules need to be intentional.

## Enterprise takeaway

> The controlled ingestion process extracts only approved utility source tables, writes raw Parquet files partitioned by load date, adds traceability metadata, validates file readability, reconciles source and raw row counts, checks AMI usage control totals, and fails safely for invalid inputs, duplicate output, unavailable databases, and corrupt files.
