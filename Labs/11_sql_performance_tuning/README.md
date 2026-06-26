# Lab 11 — SQL and Database Performance Tuning

## Answer this lab makes real

“How do you optimize SQL queries or database performance?”

## Objective

Measure a workload, diagnose its plan, apply a justified change, and prove the result without changing query correctness.

## Build

Create:

- `baseline_queries.sql`
- `tuned_queries.sql`
- `index_experiments.sql`
- `performance_report.md`

## Workloads

- Meter/date-range reading lookup
- Usage aggregation by city and date
- Work-order dashboard by status and priority
- Employee/asset/location join

## Hands-on steps

1. Capture `EXPLAIN (ANALYZE, BUFFERS)` and runtime.
2. Identify scans, join strategies, estimates, filters, and sorting.
3. Remove unnecessary columns and joins.
4. Make filters sargable.
5. Test a composite AMI index.
6. Run `ANALYZE` and compare estimates.
7. Discuss partitioning for enterprise AMI scale.
8. Retain only changes that improve the measured workload.

## Deliberate problems

- `SELECT *`
- Function applied to an indexed timestamp
- Missing composite index
- Duplicate aggregation caused by an unnecessary join
- Stale statistics

## Evidence

- Before/after plans
- Runtime and buffer table
- Accuracy/control-total comparison
- Index write-cost discussion
- Scale-out recommendations

## Enterprise debrief

Explain detection, query profile/plan analysis, reducing data scanned, join/filter optimization, indexes/statistics, platform sizing, and before/after validation.

## Completion criteria

- At least one measured improvement exists.
- Results remain identical.
- Every retained change has a workload-based rationale.
- You can translate the lesson to Snowflake pruning and warehouse behavior.

