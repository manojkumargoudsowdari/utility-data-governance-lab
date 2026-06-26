# Lab 13 — Backup, Restore, and Upgrade Validation

## Answers this lab makes real

- Backup and recovery strategy
- DBMS/data-integration upgrade validation
- Oracle, SQL Server, and SAP HANA source awareness

## Objective

Prove that the local utility source can be backed up, restored, validated, and assessed for platform or connector change impact.

## Build

Create:

- `backup_database.ps1`
- `restore_validation_database.ps1`
- `validate_restore.sql`
- `upgrade_impact_checklist.md`
- `recovery_runbook.md`

## Backup/restore exercise

1. Capture pre-backup counts, constraints, and control totals.
2. Create a logical PostgreSQL backup.
3. Restore into a separate validation database.
4. Validate schemas, tables, sequences, constraints, indexes, counts, and AMI totals.
5. Record recovery time and recovery-point assumptions.

## Upgrade exercise

Simulate a PostgreSQL image/driver/connector version change:

- inventory affected database objects and integrations;
- test compatibility in isolation;
- run schema, SQL, ingestion, and regression tests;
- compare counts, aggregates, performance, and logs;
- document rollback and post-change monitoring.

## Source-platform translation

Document how discovery and extraction would differ for Oracle, SQL Server, and SAP HANA while preserving the same mapping, validation, governance, and quality principles.

## Deliberate failure

Restore with missing configuration or test a deliberately incompatible query/driver assumption. Diagnose and correct it without affecting the primary database.

## Evidence

- Backup artifact metadata, not the backup itself in Git
- Restore logs
- Validation output
- RTO/RPO assumptions
- Upgrade regression report

## Enterprise debrief

Explain controlled reloads, point-in-time capabilities, backups, restore validation, rollback, compatibility analysis, lower-environment regression, and post-upgrade monitoring.

## Completion criteria

- Restored data reconciles.
- Constraints and indexes exist.
- Upgrade impact and rollback are documented.
- Primary data remains protected.

