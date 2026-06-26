"""
Lab 03 — Validate Raw Utility Load

Independently validates raw Parquet output against PostgreSQL source counts and
selected control totals.

Example:
    python Labs/03_controlled_ingestion/validate_raw_load.py --load-date 2026-06-25
"""

import argparse
import json
import sys
import time
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pandas as pd
from sqlalchemy import text

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_INGESTION_DIR = REPO_ROOT / "python" / "ingestion"
sys.path.insert(0, str(PYTHON_INGESTION_DIR))

from db_connection import get_postgres_engine  # noqa: E402


SOURCE_SCHEMA = "utility_source"
RAW_BASE_DIR = REPO_ROOT / "data" / "raw"

APPROVED_TABLES = {
    "service_locations": {},
    "customer_service_accounts": {},
    "hr_employees": {},
    "erp_assets": {},
    "erp_work_orders": {},
    "ami_meters": {},
    "ami_meter_readings": {"control_total_column": "usage_quantity"},
}

CONTROL_TOTAL_QUANTIZER = Decimal("0.001")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate utility raw Parquet output against source controls."
    )
    parser.add_argument(
        "--load-date",
        required=True,
        help="Load-date partition to validate in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--tables",
        default=",".join(APPROVED_TABLES.keys()),
        help="Comma-separated approved table list. Defaults to all utility tables.",
    )
    parser.add_argument(
        "--raw-base-dir",
        default=str(RAW_BASE_DIR),
        help="Base raw output directory. Defaults to data/raw.",
    )
    return parser.parse_args()


def validate_load_date(load_date):
    try:
        parsed = datetime.strptime(load_date, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("--load-date must be a valid date in YYYY-MM-DD format.") from exc

    if parsed.isoformat() != load_date:
        raise ValueError("--load-date must be a valid date in YYYY-MM-DD format.")

    return load_date


def parse_tables(tables_argument):
    requested = [table.strip() for table in tables_argument.split(",") if table.strip()]

    if not requested:
        raise ValueError("At least one table must be provided.")

    invalid = [table for table in requested if table not in APPROVED_TABLES]
    if invalid:
        allowed = ", ".join(APPROVED_TABLES.keys())
        raise ValueError(
            f"Unapproved table(s): {', '.join(invalid)}. Approved tables: {allowed}"
        )

    return requested


def raw_partition_dir(raw_base_dir, table_name, load_date):
    return Path(raw_base_dir) / SOURCE_SCHEMA / table_name / f"load_date={load_date}"


def source_count_query(table_name):
    return text(f'SELECT COUNT(*) AS row_count FROM "{SOURCE_SCHEMA}"."{table_name}"')


def source_control_total_query(table_name, control_total_column):
    return text(
        f'SELECT SUM("{control_total_column}") AS control_total '
        f'FROM "{SOURCE_SCHEMA}"."{table_name}"'
    )


def read_source_controls(engine, table_name):
    control_total_column = APPROVED_TABLES[table_name].get("control_total_column")

    with engine.connect() as connection:
        source_count = pd.read_sql_query(source_count_query(table_name), connection).iloc[0][
            "row_count"
        ]

        source_control_total = None
        if control_total_column:
            source_control_total = pd.read_sql_query(
                source_control_total_query(table_name, control_total_column),
                connection,
            ).iloc[0]["control_total"]

    return int(source_count), source_control_total


def read_raw_partition(raw_base_dir, table_name, load_date):
    partition_dir = raw_partition_dir(raw_base_dir, table_name, load_date)

    if not partition_dir.exists():
        raise FileNotFoundError(f"Raw partition does not exist: {partition_dir}")

    parquet_files = sorted(partition_dir.glob("*.parquet"))
    if not parquet_files:
        raise FileNotFoundError(f"No Parquet files found in: {partition_dir}")

    frames = [pd.read_parquet(path, engine="pyarrow") for path in parquet_files]
    raw_df = pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0]
    return raw_df, parquet_files


def normalize_control_total(value):
    if value is None:
        return None
    return Decimal(str(value)).quantize(CONTROL_TOTAL_QUANTIZER, rounding=ROUND_HALF_UP)


def validate_table(engine, raw_base_dir, table_name, load_date):
    started = time.perf_counter()
    control_total_column = APPROVED_TABLES[table_name].get("control_total_column")

    result = {
        "schema_name": SOURCE_SCHEMA,
        "table_name": table_name,
        "load_date": load_date,
        "status": "FAILED",
        "source_row_count": 0,
        "raw_row_count": 0,
        "source_control_total": "",
        "raw_control_total": "",
        "parquet_files": [],
        "duration_seconds": 0,
        "error": "",
    }

    try:
        source_count, source_control_total = read_source_controls(engine, table_name)
        raw_df, parquet_files = read_raw_partition(raw_base_dir, table_name, load_date)
        raw_count = len(raw_df)

        expected_metadata_columns = {
            "_source_system",
            "_source_schema",
            "_source_table",
            "_extraction_time_utc",
            "_load_date",
            "_run_id",
        }
        missing_metadata = sorted(expected_metadata_columns - set(raw_df.columns))
        if missing_metadata:
            raise RuntimeError(
                f"Missing raw metadata column(s): {', '.join(missing_metadata)}"
            )

        invalid_load_date_count = int((raw_df["_load_date"] != load_date).sum())
        if invalid_load_date_count:
            raise RuntimeError(
                f"Raw records with incorrect _load_date: {invalid_load_date_count}"
            )

        invalid_source_table_count = int((raw_df["_source_table"] != table_name).sum())
        if invalid_source_table_count:
            raise RuntimeError(
                f"Raw records with incorrect _source_table: {invalid_source_table_count}"
            )

        raw_control_total = None
        if control_total_column:
            raw_control_total = raw_df[control_total_column].sum()
            if normalize_control_total(source_control_total) != normalize_control_total(raw_control_total):
                raise RuntimeError(
                    "Control-total mismatch: "
                    f"source={source_control_total}, raw={raw_control_total}"
                )

        if source_count != raw_count:
            raise RuntimeError(f"Row-count mismatch: source={source_count}, raw={raw_count}")

        result.update(
            {
                "status": "SUCCESS",
                "source_row_count": source_count,
                "raw_row_count": raw_count,
                "source_control_total": source_control_total if source_control_total is not None else "",
                "raw_control_total": raw_control_total if raw_control_total is not None else "",
                "parquet_files": [str(path) for path in parquet_files],
            }
        )
    except Exception as exc:
        result["error"] = str(exc)

    result["duration_seconds"] = round(time.perf_counter() - started, 3)
    return result


def main():
    run_started = time.perf_counter()
    args = parse_args()

    try:
        load_date = validate_load_date(args.load_date)
        selected_tables = parse_tables(args.tables)
    except Exception as exc:
        print(f"CONFIGURATION_FAILED: {exc}", file=sys.stderr)
        return 1

    try:
        engine = get_postgres_engine()
    except Exception as exc:
        print(f"DATABASE_CONNECTION_FAILED: {exc}", file=sys.stderr)
        return 1

    results = [
        validate_table(engine, args.raw_base_dir, table_name, load_date)
        for table_name in selected_tables
    ]

    failed = [result for result in results if result["status"] != "SUCCESS"]
    summary = {
        "status": "FAILED" if failed else "SUCCESS",
        "source_schema": SOURCE_SCHEMA,
        "load_date": load_date,
        "duration_seconds": round(time.perf_counter() - run_started, 3),
        "tables": results,
    }

    print(json.dumps(summary, indent=2, default=str))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
