# Lab 12 — Snowflake Platform Patterns

## Answer this lab makes real

“What is your Snowflake experience, and how would you use it here?”

## Objective

Translate the local utility platform into Snowflake-native object, loading, transformation, security, performance, and recovery patterns. Execute in a Snowflake trial/sandbox if available; otherwise produce executable SQL and clearly label unexecuted portions.

## Build

Create:

- `01_objects.sql`
- `02_stage_and_copy.sql`
- `03_incremental_merge.sql`
- `04_rbac_masking.sql`
- `05_time_travel_clone.sql`
- `06_performance_queries.sql`
- `snowflake_architecture.md`
- `execution_evidence.md`

## Required topics

- Databases and schemas for raw, standardized, curated, reporting, and governance
- Virtual warehouses and auto-suspend
- File format, stage, and `COPY INTO`
- Load history and rejected records
- Incremental `MERGE`
- Streams/Tasks design
- Role hierarchy and masking policy
- Secure views
- Time Travel and zero-copy clone
- Query History, Query Profile, pruning, clustering, spilling, and warehouse sizing

## Deliberate failures

- Bad staged row
- Duplicate-match `MERGE`
- Unauthorized role
- Accidental update recovered through Time Travel/clone
- Under-sized warehouse or poorly pruning query

## Evidence

- Executed SQL or clearly marked runnable design
- Load and merge results
- Role tests
- Recovery demonstration
- Query profile observations

## Enterprise debrief

Walk through how Snowflake would centralize ERP, HR, AMI, and reporting data while supporting governed facts/dimensions, incremental loads, quality gates, RBAC, performance, and recovery.

## Completion criteria

- The design uses Snowflake-native concepts rather than PostgreSQL terminology alone.
- Security, performance, loading, and recovery are all demonstrated or explicitly designed.
- Any simulation is honestly labeled.

