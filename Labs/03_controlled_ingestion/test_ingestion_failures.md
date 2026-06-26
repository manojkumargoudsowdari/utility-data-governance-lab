# Lab 03 Failure Practice

Use this file to intentionally test controlled failures.

Run these commands from the repository root.

## 1. Unapproved table

Command:

```powershell
python Labs/03_controlled_ingestion/run_utility_ingestion.py --load-date 2026-06-25 --tables customers
```

Expected result:

```text
CONFIGURATION_FAILED
Unapproved table(s): customers
```

Why this matters:

> Production ingestion should not accept arbitrary table names. Approved source objects should be controlled through configuration or metadata.

## 2. Invalid load date

Command:

```powershell
python Labs/03_controlled_ingestion/run_utility_ingestion.py --load-date 06-25-2026
```

Expected result:

```text
CONFIGURATION_FAILED
--load-date must be a valid date in YYYY-MM-DD format
```

Why this matters:

> Bad partition dates create inconsistent raw directory layouts and make reruns difficult to audit.

## 3. Existing load-date output

First run:

```powershell
python Labs/03_controlled_ingestion/run_utility_ingestion.py --load-date 2026-06-25 --tables ami_meters
```

Second run with the same table and same load date:

```powershell
python Labs/03_controlled_ingestion/run_utility_ingestion.py --load-date 2026-06-25 --tables ami_meters
```

Expected result on the second run:

```text
CONFIGURATION_FAILED
Existing load-date output found. Refusing to overwrite raw data
```

Why this matters:

> Raw ingestion should avoid silent overwrites. If a rerun is needed, the team should intentionally archive/delete the prior output or use a clearly controlled rerun strategy.

## 4. Database unavailable

Stop PostgreSQL:

```powershell
docker compose stop postgres
```

Run ingestion:

```powershell
python Labs/03_controlled_ingestion/run_utility_ingestion.py --load-date 2026-06-26 --tables service_locations
```

Expected result:

```text
status: FAILED
table_name: __connection__
```

Restart PostgreSQL:

```powershell
docker compose start postgres
```

Why this matters:

> A production pipeline should fail clearly if a source system is unavailable.

## 5. Corrupt or unreadable output

After a successful run, replace one Parquet file with invalid content or rename it temporarily.

Then run:

```powershell
python Labs/03_controlled_ingestion/validate_raw_load.py --load-date 2026-06-25 --tables ami_meters
```

Expected result:

```text
status: FAILED
```

Why this matters:

> Writing a file is not enough. A controlled pipeline should read the file back and confirm it is usable.

## Enterprise implementation phrasing

> I tested failure behavior by intentionally passing an unapproved table, invalid load date, duplicate load-date output, unavailable database, and corrupt raw output. Each failure is designed to stop safely, produce a clear error, and return a non-zero exit code so orchestration tools can detect the failed run.
