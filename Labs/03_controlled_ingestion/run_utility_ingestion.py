"""
Lab 03 — Controlled Source-to-Raw Utility Ingestion

Extracts approved PostgreSQL utility source tables into raw Parquet files with
load-date partitioning, metadata columns, read-back validation, and audit output.

Example:
    python Labs/03_controlled_ingestion/run_utility_ingestion.py --load-date 2026-06-25
"""

import argparse
import csv
import json
import sys
import time
import uuid
from datetime import date, datetime, timezone
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
LOG_DIR = REPO_ROOT / "logs" / "ingestion"

APPROVED_TABLES = {
    "service_locations": {
        "primary_key": "service_location_id",
        "source_system": "utility_location_master",
    },
    "customer_service_accounts": {
        "primary_key": "customer_service_account_id",
        "source_system": "customer_information_system",
    },
    "hr_employees": {
        "primary_key": "employee_id",
        "source_system": "human_resources",
    },
    "erp_assets": {
        "primary_key": "asset_id",
        "source_system": "enterprise_resource_planning",
    },
    "erp_work_orders": {
        "primary_key": "work_order_id",
        "source_system": "enterprise_resource_planning",
    },
    "ami_meters": {
        "primary_key": "meter_id",
        "source_system": "advanced_metering_infrastructure",
    },
    "ami_meter_readings": {
        "primary_key": "reading_id",
        "source_system": "advanced_metering_infrastructure",
        "control_total_column": "usage_quantity",
    },
}

CONTROL_TOTAL_QUANTIZER = Decimal("0.001")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract approved utility PostgreSQL source tables to raw Parquet."
    )
    parser.add_argument(
        "--load-date",
        default=date.today().isoformat(),
        help="Load-date partition in YYYY-MM-DD format. Defaults to today.",
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
    parser.add_argument(
        "--log-dir",
        default=str(LOG_DIR),
        help="Audit log directory. Defaults to logs/ingestion.",
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


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def output_dir_for(raw_base_dir, table_name, load_date):
    return Path(raw_base_dir) / SOURCE_SCHEMA / table_name / f"load_date={load_date}"


def preflight_output_paths(raw_base_dir, table_names, load_date):
    existing = [
        output_dir_for(raw_base_dir, table_name, load_date)
        for table_name in table_names
        if output_dir_for(raw_base_dir, table_name, load_date).exists()
    ]

    if existing:
        formatted = "\n".join(str(path) for path in existing)
        raise FileExistsError(
            "Existing load-date output found. Refusing to overwrite raw data:\n"
            f"{formatted}\n"
            "Use a new --load-date or intentionally archive/delete the old output."
        )


def source_count_query(table_name):
    return text(f'SELECT COUNT(*) AS row_count FROM "{SOURCE_SCHEMA}"."{table_name}"')


def source_control_total_query(table_name, control_total_column):
    return text(
        f'SELECT SUM("{control_total_column}") AS control_total '
        f'FROM "{SOURCE_SCHEMA}"."{table_name}"'
    )


def extract_query(table_name, primary_key):
    return text(
        f'SELECT * FROM "{SOURCE_SCHEMA}"."{table_name}" '
        f'ORDER BY "{primary_key}"'
    )


def read_source_table(engine, table_name):
    table_config = APPROVED_TABLES[table_name]
    primary_key = table_config["primary_key"]

    with engine.connect() as connection:
        source_count = pd.read_sql_query(source_count_query(table_name), connection).iloc[0][
            "row_count"
        ]
        df = pd.read_sql_query(extract_query(table_name, primary_key), connection)

        control_total_column = table_config.get("control_total_column")
        source_control_total = None
        if control_total_column:
            source_control_total = pd.read_sql_query(
                source_control_total_query(table_name, control_total_column),
                connection,
            ).iloc[0]["control_total"]

    return df, int(source_count), source_control_total


def add_raw_metadata(df, table_name, load_date, run_id, extraction_time):
    table_config = APPROVED_TABLES[table_name]
    enriched = df.copy()
    enriched["_source_system"] = table_config["source_system"]
    enriched["_source_schema"] = SOURCE_SCHEMA
    enriched["_source_table"] = table_name
    enriched["_extraction_time_utc"] = extraction_time
    enriched["_load_date"] = load_date
    enriched["_run_id"] = run_id
    return enriched


def write_parquet(df, raw_base_dir, table_name, load_date, run_id):
    table_output_dir = output_dir_for(raw_base_dir, table_name, load_date)
    table_output_dir.mkdir(parents=True, exist_ok=False)
    output_path = table_output_dir / f"{table_name}_{run_id}.parquet"
    df.to_parquet(output_path, index=False, engine="pyarrow")
    return output_path


def validate_written_file(output_path, expected_count, control_total_column=None):
    readback_df = pd.read_parquet(output_path, engine="pyarrow")
    parquet_count = len(readback_df)

    raw_control_total = None
    if control_total_column:
        raw_control_total = readback_df[control_total_column].sum()

    count_matches = parquet_count == expected_count
    return parquet_count, raw_control_total, count_matches


def normalize_control_total(value):
    if value is None:
        return None
    return Decimal(str(value)).quantize(CONTROL_TOTAL_QUANTIZER, rounding=ROUND_HALF_UP)


def build_summary_paths(log_dir, run_id):
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    csv_path = log_path / f"utility_ingestion_summary_{run_id}.csv"
    json_path = log_path / f"utility_ingestion_summary_{run_id}.json"
    return csv_path, json_path


def write_summary(summary, csv_path, json_path):
    rows = summary["tables"]
    fieldnames = [
        "run_id",
        "load_date",
        "schema_name",
        "table_name",
        "status",
        "source_row_count",
        "raw_row_count",
        "source_control_total",
        "raw_control_total",
        "output_path",
        "duration_seconds",
        "error",
    ]

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with json_path.open("w", encoding="utf-8") as json_file:
        json.dump(summary, json_file, indent=2, default=str)


def ingest_table(engine, raw_base_dir, table_name, load_date, run_id):
    table_started = time.perf_counter()
    extraction_time = utc_now_iso()
    control_total_column = APPROVED_TABLES[table_name].get("control_total_column")

    row = {
        "run_id": run_id,
        "load_date": load_date,
        "schema_name": SOURCE_SCHEMA,
        "table_name": table_name,
        "status": "FAILED",
        "source_row_count": 0,
        "raw_row_count": 0,
        "source_control_total": "",
        "raw_control_total": "",
        "output_path": "",
        "duration_seconds": 0,
        "error": "",
    }

    try:
        source_df, source_count, source_control_total = read_source_table(engine, table_name)
        raw_df = add_raw_metadata(source_df, table_name, load_date, run_id, extraction_time)
        output_path = write_parquet(raw_df, raw_base_dir, table_name, load_date, run_id)
        raw_count, raw_control_total, count_matches = validate_written_file(
            output_path,
            source_count,
            control_total_column,
        )

        control_total_matches = True
        if control_total_column:
            control_total_matches = (
                normalize_control_total(source_control_total)
                == normalize_control_total(raw_control_total)
            )

        if not count_matches:
            raise RuntimeError(
                f"Row-count mismatch: source={source_count}, raw={raw_count}"
            )

        if not control_total_matches:
            raise RuntimeError(
                "Control-total mismatch: "
                f"source={source_control_total}, raw={raw_control_total}"
            )

        row.update(
            {
                "status": "SUCCESS",
                "source_row_count": source_count,
                "raw_row_count": raw_count,
                "source_control_total": source_control_total if source_control_total is not None else "",
                "raw_control_total": raw_control_total if raw_control_total is not None else "",
                "output_path": str(output_path),
            }
        )
    except Exception as exc:
        row["error"] = str(exc)

    row["duration_seconds"] = round(time.perf_counter() - table_started, 3)
    return row


def main():
    run_started = time.perf_counter()
    run_id = str(uuid.uuid4())
    args = parse_args()

    try:
        load_date = validate_load_date(args.load_date)
        selected_tables = parse_tables(args.tables)
        preflight_output_paths(args.raw_base_dir, selected_tables, load_date)
    except Exception as exc:
        print(f"CONFIGURATION_FAILED: {exc}", file=sys.stderr)
        return 1

    csv_path, json_path = build_summary_paths(args.log_dir, run_id)

    summary = {
        "run_id": run_id,
        "status": "FAILED",
        "source_schema": SOURCE_SCHEMA,
        "load_date": load_date,
        "selected_tables": selected_tables,
        "started_at_utc": utc_now_iso(),
        "finished_at_utc": "",
        "duration_seconds": 0,
        "summary_csv": str(csv_path),
        "summary_json": str(json_path),
        "tables": [],
    }

    try:
        engine = get_postgres_engine()
    except Exception as exc:
        summary["tables"].append(
            {
                "run_id": run_id,
                "load_date": load_date,
                "schema_name": SOURCE_SCHEMA,
                "table_name": "__connection__",
                "status": "FAILED",
                "source_row_count": 0,
                "raw_row_count": 0,
                "source_control_total": "",
                "raw_control_total": "",
                "output_path": "",
                "duration_seconds": 0,
                "error": str(exc),
            }
        )
        summary["finished_at_utc"] = utc_now_iso()
        summary["duration_seconds"] = round(time.perf_counter() - run_started, 3)
        write_summary(summary, csv_path, json_path)
        print(json.dumps(summary, indent=2, default=str))
        return 1

    for table_name in selected_tables:
        row = ingest_table(engine, args.raw_base_dir, table_name, load_date, run_id)
        summary["tables"].append(row)
        print(
            f"{row['status']} {SOURCE_SCHEMA}.{table_name} "
            f"source_rows={row['source_row_count']} raw_rows={row['raw_row_count']} "
            f"duration_seconds={row['duration_seconds']}"
        )

    failed_rows = [row for row in summary["tables"] if row["status"] != "SUCCESS"]
    summary["status"] = "FAILED" if failed_rows else "SUCCESS"
    summary["finished_at_utc"] = utc_now_iso()
    summary["duration_seconds"] = round(time.perf_counter() - run_started, 3)
    write_summary(summary, csv_path, json_path)

    print(json.dumps(summary, indent=2, default=str))

    return 1 if failed_rows else 0


if __name__ == "__main__":
    sys.exit(main())
