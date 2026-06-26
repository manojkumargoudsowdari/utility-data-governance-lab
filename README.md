# Utility Data Governance Lab

This repository is a local, hands-on utility data governance project that simulates enterprise data platform work on a developer machine.

It simulates scattered utility operational data across:

- Service locations
- Customer service accounts
- HR employees
- ERP assets
- ERP work orders
- AMI meters
- AMI meter readings

PostgreSQL is used locally to simulate source systems and warehouse-style schemas. The labs use SQL, Python, and local files to practice source discovery, ingestion, validation, reconciliation, modeling, lineage, access control, incident response, and governance concepts.

## Active architecture

```text
PostgreSQL utility_source schema
        ↓
Lab 1: source discovery
        ↓
Lab 2: curated dimensional model in utility_curated
        ↓
Lab 3: controlled source-to-raw ingestion
        ↓
Future labs: standardization, data quality, lineage, incidents, RBAC, tuning
```

## Main folders

| Folder | Purpose |
|---|---|
| `postgres/` | PostgreSQL utility source schema |
| `data-generator/` | Synthetic utility data generator |
| `Labs/` | Practical enterprise data platform lab exercises |
| `python/ingestion/` | Shared PostgreSQL connection helper |
| `data/raw/` | Local raw landing zone, ignored by Git |
| `data/standardized/` | Local standardized output zone, ignored by Git |
| `data/curated/` | Local curated output zone, ignored by Git |
| `logs/` | Runtime logs and summaries, ignored by Git |

## Local setup

Create a local `.env` file from `.env.example`.

Required variables:

```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=utility_governance_lab
POSTGRES_USER=utility_user
POSTGRES_PASSWORD=<your local password>
```

Start PostgreSQL:

```powershell
docker compose up -d
```

Apply schema:

```powershell
Get-Content .\postgres\schema.sql | docker compose exec -T postgres psql -U utility_user -d utility_governance_lab
```

Generate synthetic source data:

```powershell
python data-generator/generate_utility_data.py
```

## Current source data volumes

| Source table | Row count |
|---|---:|
| `service_locations` | 500 |
| `customer_service_accounts` | 650 |
| `hr_employees` | 120 |
| `erp_assets` | 800 |
| `erp_work_orders` | 600 |
| `ami_meters` | 1,000 |
| `ami_meter_readings` | 30,000 |

## Lab progress

| Lab | Topic | Status |
|---|---|---|
| 01 | Source-system discovery | Complete |
| 02 | Utility data modeling | Complete |
| 03 | Controlled source-to-raw ingestion | Scripts created |
| 04+ | Standardization, quality, lineage, incidents, RBAC, tuning | Planned |

## Run Lab 3 ingestion

Use a load date that does not already exist under `data/raw`.

```powershell
python Labs/03_controlled_ingestion/run_utility_ingestion.py --load-date 2026-06-26
```

Validate the raw load:

```powershell
python Labs/03_controlled_ingestion/validate_raw_load.py --load-date 2026-06-26
```

## Enterprise simulation focus

This project provides practical implementation evidence for enterprise-style data engineering work:

- How to discover source systems before ingestion
- How to identify grain, keys, and relationships
- How to model dimensions and facts
- How to reconcile source and target row counts
- How to validate AMI usage control totals
- How to design controlled, auditable ingestion
- How to separate operational source data from curated analytical data
