# Lab 07 — AMI Time-Series and Incremental Processing

## Answer this lab makes real

“What is AMI data, and how would you design its pipeline?”

## Objective

Treat AMI readings as high-volume, time-based operational data. Implement incremental processing, deduplication, late-arriving data handling, and point-in-time aggregation.

## Build

Create:

- `generate_incremental_ami_batch.py`
- `process_incremental_ami.py`
- `validate_incremental_ami.sql`
- `ami_design_notes.md`

## Exercise

1. Establish an initial high-water mark.
2. Generate a new reading day.
3. Include duplicates, one correction, one late reading, one missing reading, and one error status.
4. Process the batch idempotently.
5. Update daily usage only for affected meter/date partitions.
6. Advance the watermark only after validation succeeds.

## Required design topics

- Business key for a reading
- Event time versus ingestion time
- Deduplication ordering
- Late-data lookback window
- Missing and estimated readings
- Usage units and conversion policy
- Partitioning by reading or load date
- Meter/location/customer relationship history
- Sensitive usage access

## Deliberate failure

Fail after data implementation practice but before watermark commit. Rerun and prove no logical duplicates or data loss.

## Evidence

- Before/after watermark
- Incremental counts
- Late/corrected record behavior
- Duplicate check
- Daily control-total reconciliation

## Enterprise debrief

Explain why AMI is operational time-series data, its major quality and scale risks, and how Bronze/Silver/Gold, incremental processing, partitioning, reconciliation, and RBAC address them.

## Completion criteria

- Reprocessing is idempotent.
- Late and corrected records update the correct day.
- Watermark safety is demonstrated.
- Grain remains one meter/date in the daily fact.

