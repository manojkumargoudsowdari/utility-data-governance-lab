# Lab 04 — PySpark Lakehouse Standardization

## Answer this lab makes real

“What is your experience with Databricks, PySpark, Delta Lake, and Bronze/Silver/Gold architecture?”

## Objective

Use PySpark to turn immutable raw utility data into typed, normalized, quality-controlled standardized datasets and then publish selected Gold models.

## Build

Create:

- `standardize_utility_data.py`
- `utility_schema_contracts.py`
- `inject_bad_raw_data.py`
- `lakehouse_walkthrough.md`

Reuse `spark/jobs/process_raw_to_standardized.py` and shared Spark utilities where practical.

## Silver rules

- Explicit schemas
- Trim strings and convert blanks to null
- Normalize controlled domains
- Cast dates, timestamps, IDs, and decimals
- Add source/load/run metadata
- Add deterministic record hash
- Separate accepted and rejected rows
- Reconcile input = accepted + rejected

## Gold exercise

Publish:

- daily meter usage
- meter dimension
- service-location dimension
- work-order fact

## Deliberate failures

- Missing required column
- Invalid timestamp
- Invalid decimal
- New nullable column
- Breaking datatype change

## Performance practice

Inspect partitions, joins, shuffle behavior, file counts, and broadcast suitability. Explain how Delta `MERGE`, schema enforcement, and table history would replace or extend local Parquet behavior.

## Enterprise debrief

Demonstrate Bronze traceability, Silver standardization and quarantine, and Gold business models. Explain schema evolution, idempotency, partitioning, and late-arriving data.

## Completion criteria

- Clean data produces zero rejects.
- Injected bad data is visible and controlled.
- Counts reconcile.
- You can explain which parts are local PySpark/Parquet and which are Databricks/Delta patterns.

