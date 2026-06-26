# Utility Data Governance Enterprise Labs

These labs simulate enterprise utility data platform work locally. The goal is to build, break, validate, and explain real implementation behavior using PostgreSQL, Python, SQL, and local data zones.

## Working method

For every lab:

1. Read the lab `README.md`.
2. Implement the requested scripts inside that lab folder.
3. Run the happy path.
4. Run the deliberate failure scenario.
5. save only lightweight evidence such as SQL output, Markdown notes, or screenshots.
6. Complete the enterprise debrief in your own words.

Do not commit secrets, `.env`, database volumes, generated Parquet data, or logs containing credentials.

## Lab sequence

| Lab | Practical theme | Enterprise capability reinforced |
|---|---|---|
| [01](01_source_system_discovery/README.md) | Source discovery and centralization plan | Centralizing scattered ERP, HR, AMI, and operational data |
| [02](02_utility_data_modeling/README.md) | Logical and physical utility modeling | Explain a data model; AMI and utility modeling |
| [03](03_controlled_ingestion/README.md) | Controlled source-to-raw ingestion | Centralization; Python; auditability |
| [04](04_lakehouse_standardization/README.md) | Bronze, Silver, and Gold with PySpark | Databricks, PySpark, Delta/lakehouse |
| [05](05_data_quality_reconciliation/README.md) | Quality gates and reconciliation | Data quality and source-to-target validation |
| [06](06_mapping_lineage_impact/README.md) | Mapping, lineage, and impact analysis | Source-to-target mapping; lineage; collaboration |
| [07](07_ami_incremental_processing/README.md) | AMI time-series and incremental processing | AMI design; late data; idempotency |
| [08](08_production_incident_recovery/README.md) | Production incident diagnosis and recovery | Troubleshooting; ownership; operational excellence |
| [09](09_schema_change_sdlc/README.md) | DDL and schema evolution through SDLC | Schema changes; release validation; collaboration |
| [10](10_rbac_sensitive_data/README.md) | RBAC, masking, and least privilege | HR/customer/AMI security |
| [11](11_sql_performance_tuning/README.md) | Query plans, indexes, and measured tuning | SQL and database performance |
| [12](12_snowflake_platform_patterns/README.md) | Snowflake-native platform patterns | Snowflake experience; recovery; performance |
| [13](13_backup_restore_upgrade/README.md) | Backup, restore, and upgrade validation | Backup/recovery; DBMS and integration upgrades |
| [14](14_enterprise_capstone/README.md) | End-to-end enterprise platform demonstration | Architecture walkthrough; operational controls; implementation evidence |

## Existing repository assets

The labs should reuse the project instead of creating disconnected demos:

- `postgres/schema.sql` and `data-generator/generate_utility_data.py`
- `python/ingestion/`
- `Labs/`
- `data/raw/`, `data/standardized/`, and `data/curated/`
- `logs/`

## Definition of done

A lab is complete only when you can:

- demonstrate the result locally;
- explain the business problem before discussing the technology;
- state the data grain, keys, quality controls, security, and operational risks;
- show one controlled failure and the recovery;
- connect the evidence to a concise enterprise implementation explanation.
