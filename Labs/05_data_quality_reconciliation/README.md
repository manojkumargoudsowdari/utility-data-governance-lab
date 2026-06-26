# Lab 05 — Data Quality, Exceptions, and Reconciliation

## Answer this lab makes real

“How do you ensure data quality and reconciliation before publishing data?”

## Objective

Implement layered quality gates that prevent untrusted utility data from being published while retaining actionable exception evidence.

## Build

Create:

- `utility_dq_rules.sql`
- `run_utility_dq.py`
- `inject_quality_defects.sql`
- `dq_runbook.md`

Reuse existing SQL and PySpark DQ frameworks where possible.

## Required rule dimensions

- Completeness
- Uniqueness
- Validity
- Consistency
- Referential integrity
- Timeliness
- Reconciliation

## Required controls

- Source/raw/standardized/curated row counts
- AMI usage control totals with decimal-safe tolerance
- Duplicate meter/date readings
- Missing, error, negative, and future readings
- Meter-to-location integrity
- Work-order status/date consistency
- Asset and employee relationships
- Account lifecycle dates

Every result should include rule ID, dataset, dimension, severity, threshold, observed value, status, run ID, and execution timestamp.

## Deliberate failures

Inject at least:

- one duplicate reading;
- one negative usage value;
- one orphan or invalid relationship;
- one reconciliation mismatch.

## Evidence

- Clean run summary
- Failed run summary
- Exception records
- Control-total comparison
- Remediation notes

## Enterprise debrief

Explain layered validation, blocking versus warning rules, source-to-target reconciliation, audit metadata, exception handling, backfills, and why reruns must be idempotent.

## Completion criteria

- Clean data passes all blocking rules.
- Defects fail the intended rules.
- Exceptions identify affected business records.
- Publication is blocked on critical failure.

