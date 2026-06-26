# Lab 01 Observations

## Environment confirmed

- Database: `utility_governance_lab`
- User: `utility_user`
- Schema: `utility_source`
- Seven utility source tables are available.

## Source volumes

| Source table | Row count |
|---|---:|
| `service_locations` | 500 |
| `customer_service_accounts` | 650 |
| `hr_employees` | 120 |
| `erp_assets` | 800 |
| `erp_work_orders` | 600 |
| `ami_meters` | 1,000 |
| `ami_meter_readings` | 30,000 |

## AMI history

- Earliest reading: May 21, 2026
- Latest reading: June 19, 2026
- Distinct reading days: 30
- Average readings per day: 1,000
- The counts are consistent with one daily reading for each of 1,000 meters.

## Source classification

| Source | Recommended ingestion | Security priority | Main quality risk |
|---|---|---|---|
| `service_locations` | Incremental using `updated_at` | High | Missing or invalid address; duplicate location |
| `customer_service_accounts` | Incremental using `updated_at` | High | Invalid location relationship or account dates |
| `hr_employees` | Incremental using `updated_at` | High | Sensitive access or invalid manager relationship |
| `erp_assets` | Incremental using `updated_at` | Medium | Invalid location or asset status |
| `erp_work_orders` | Incremental using `updated_at` | Medium | Invalid asset or employee; inconsistent status dates |
| `ami_meters` | Incremental using `updated_at` | High | Invalid location relationship or duplicate meter |
| `ami_meter_readings` | Time-based incremental load with a lookback window | High | Duplicate, missing, late, erroneous, or negative readings |

## Key observations

### PostgreSQL versus Snowflake in this lab

This local lab uses PostgreSQL as a practical substitute for an enterprise warehouse such as Snowflake.

PostgreSQL is used here because it runs locally in Docker and supports the core concepts needed for enterprise platform practice:

- Schemas
- Tables
- Primary keys and foreign keys
- Constraints
- SQL querying
- Metadata discovery through `information_schema`
- Data validation and reconciliation

In a real production environment, the same concepts would often be implemented in Snowflake, Databricks, Synapse, or another enterprise data platform. The production version would likely separate data into layers such as raw, staged, curated, and reporting schemas.

Example production mapping:

| Lab concept | Local implementation | Production equivalent |
|---|---|---|
| Source-system tables | PostgreSQL `utility_source` schema | ERP, HR, AMI, CRM, GIS, or work-order systems |
| Metadata discovery | PostgreSQL `information_schema` | Snowflake `INFORMATION_SCHEMA` or data catalog |
| Row-count reconciliation | SQL `count(*)` checks | Pipeline audit tables, Snowflake queries, orchestration logs |
| Sensitive-data review | Manual table/column inspection | RBAC, masking policies, column tags, access audits |
| Data-quality checks | SQL validation queries | dbt tests, Great Expectations, Snowflake tasks, Databricks jobs |

Enterprise implementation phrasing:

> In my local lab, I used PostgreSQL to simulate source systems and warehouse-style schemas. In production, I would apply the same discovery, reconciliation, metadata review, data-quality, and governance concepts in Snowflake or Databricks using raw, staged, curated, and reporting layers.

### Production analogy for reconciled row counts

In this lab, the generator created known volumes, so reconciliation meant checking expected row counts against actual table row counts.

In a real production system, the same idea would compare source-system counts, ingestion logs, and target-table counts. For example:

- The AMI source system reports that it exported 1,000,000 meter readings for June 19.
- The ingestion pipeline log says it received 1,000,000 records.
- The raw landing table contains 1,000,000 records.
- The curated target table contains 999,850 records.

That difference means 150 records were dropped, rejected, duplicated, filtered, or failed validation. A data engineer would investigate the reject table, pipeline logs, duplicate rules, schema errors, late-arriving records, and transformation filters before marking the load as complete.

The business analogy is like receiving boxes in a warehouse. If the shipping manifest says 100 boxes were sent, the receiving dock should count 100 boxes, and the inventory system should also show 100 boxes processed. If only 98 appear in inventory, the shipment is not fully reconciled.

### AMI ingestion versus employee ingestion

AMI readings are continuous, high-volume time-series events. They require event-time processing, incremental extraction, deduplication, late-arrival handling, and a controlled lookback window.

Employee data is lower-volume master data that changes less frequently. It can primarily use `updated_at` to identify inserted or changed records.

### Sensitive-data priorities

- HR data includes employee identity and employment details.
- Customer data includes names and account numbers.
- Service-location data contains addresses and geographic coordinates.
- AMI data contains detailed usage patterns linked to meters and locations.

These domains require least-privilege access, restricted or masked views, audit logging, and aggregated access when record-level details are unnecessary.

### Why discovery comes before ingestion

Centralization should not begin by copying every available table. Source discovery must first establish:

- Business meaning
- Record grain
- Primary and business keys
- Relationships
- Ownership and stewardship
- Volume and growth
- Freshness requirements
- Sensitive fields
- Data-quality risks

These findings determine the ingestion method, security controls, target model, validation rules, partitioning, and refresh schedule.

## Enterprise takeaway

> I begin centralization with source discovery rather than immediately copying data. I inventory the systems and understand ownership, grain, keys, relationships, volumes, freshness, sensitivity, and quality risks. I then choose an ingestion strategy appropriate to each source. Employee master data can use `updated_at`-based incremental extraction, while high-volume AMI readings require event-time processing, deduplication, late-data handling, and controlled lookback windows.
