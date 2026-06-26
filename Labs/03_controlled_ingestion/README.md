# Lab 03 — Controlled Source-to-Raw Ingestion

## Answers this lab makes real

- Centralizing scattered data
- Python ingestion and automation
- Auditability and production reliability

## Objective

Extend the existing Python ingestion process so all utility sources land in a controlled raw zone with traceability and source-to-target count reconciliation.

## Build

Create:

- `run_utility_ingestion.py`
- `validate_raw_load.py`
- `ingestion_contract.md`
- `test_ingestion_failures.md`

Reuse connection handling from `python/ingestion/`. Write outputs to the existing raw data convention rather than inventing a second platform.

## Required behavior

- Approved schema/table whitelist
- Validated `load_date`
- Schema-qualified PostgreSQL extraction
- Raw Parquet partitioned by load date
- Source metadata: source system, schema, table, extraction time, load date, run ID
- Read-back validation
- Source/raw row-count and AMI usage-total reconciliation
- Structured summary with status, duration, counts, and error
- Non-zero exit on failure

## Deliberate failures

- Unapproved table
- Invalid date
- Database unavailable
- Existing load-date output
- Corrupt or unreadable output

## Evidence

- Raw directory layout
- Summary output
- Count reconciliation
- Failure output
- Rerun behavior

## Enterprise debrief

Explain why the raw layer preserves source meaning, why identifiers must come from a whitelist, what makes the load auditable, and how reruns avoid duplicate or ambiguous output.

## Completion criteria

- All seven sources load.
- Counts and selected control totals match.
- Invalid inputs fail safely.
- No credentials appear in code or logs.

