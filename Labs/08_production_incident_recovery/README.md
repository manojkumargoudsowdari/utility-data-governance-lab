# Lab 08 — Production Incident Diagnosis and Recovery

## Answers this lab makes real

- “Tell me about a production issue.”
- Ownership and operational excellence behavioral themes

## Objective

Reproduce a duplicate-data incident caused by flawed incremental logic, diagnose it using evidence, correct the data, and prevent recurrence.

## Build

Create:

- `create_duplicate_incident.py`
- `diagnose_incident.sql`
- `repair_incremental_load.py`
- `incident_report.md`
- `monitoring_rule.md`

## Scenario

A rerun introduces duplicate meter/date records or duplicate work orders into a curated/reporting model. A dashboard total no longer matches the source.

## Response sequence

1. Record detection time, impact, and affected consumers.
2. Check recent releases, job logs, counts, and aggregates.
3. Trace the defect through lineage.
4. Identify the faulty business key or merge logic.
5. Contain publication.
6. Repair current data with a controlled backfill.
7. correct incremental/deduplication logic.
8. Reconcile and obtain simulated business validation.
9. Add prevention and monitoring.

## Evidence

- Failed reconciliation
- Root-cause query
- Before/after duplicate counts
- Corrected metrics
- Timeline, RCA, corrective action, preventive action

## Enterprise debrief

Tell the story using Situation, Impact, Diagnosis, Root Cause, Resolution, Validation, and Prevention. Avoid presenting it as only a coding bug.

## Completion criteria

- The incident is reproducible.
- The repair restores trusted totals.
- Rerun no longer creates duplicates.
- Monitoring detects a recurrence before reporting publication.

