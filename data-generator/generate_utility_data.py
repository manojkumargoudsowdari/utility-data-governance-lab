"""Generate and load synthetic utility source-system data into PostgreSQL."""

import os
import random
import sys
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

import psycopg2
from dotenv import load_dotenv
from faker import Faker
from psycopg2.extras import execute_values


Faker.seed(42)
random.seed(42)
fake = Faker("en_US")

NUM_SERVICE_LOCATIONS = 500
NUM_CUSTOMER_SERVICE_ACCOUNTS = 650
NUM_HR_EMPLOYEES = 120
NUM_ERP_ASSETS = 800
NUM_ERP_WORK_ORDERS = 600
NUM_AMI_METERS = 1_000
READING_DAYS = 30
NUM_AMI_METER_READINGS = NUM_AMI_METERS * READING_DAYS

UTILITY_SCHEMA = "utility_source"
UTILITY_TABLES = [
    "service_locations",
    "customer_service_accounts",
    "hr_employees",
    "erp_assets",
    "erp_work_orders",
    "ami_meters",
    "ami_meter_readings",
]

FLORIDA_CITIES = [
    ("Tampa", "33602"),
    ("Temple Terrace", "33617"),
    ("Brandon", "33511"),
    ("Riverview", "33578"),
    ("Clearwater", "33755"),
    ("St. Petersburg", "33701"),
    ("Lakeland", "33801"),
    ("Plant City", "33563"),
    ("Wesley Chapel", "33544"),
    ("Lutz", "33548"),
]

SERVICE_TYPES = ["GAS_RESIDENTIAL", "GAS_COMMERCIAL", "GAS_INDUSTRIAL"]
SERVICE_STATUSES = ["ACTIVE", "INACTIVE", "PENDING", "RETIRED"]
CUSTOMER_TYPES = ["RESIDENTIAL", "COMMERCIAL", "INDUSTRIAL"]
ACCOUNT_STATUSES = ["ACTIVE", "INACTIVE", "CLOSED", "PENDING"]
EMPLOYMENT_STATUSES = ["ACTIVE", "INACTIVE", "TERMINATED", "LEAVE"]
ASSET_TYPES = [
    "SERVICE_LINE",
    "REGULATOR",
    "VALVE",
    "MAIN",
    "RISER",
    "PRESSURE_SENSOR",
]
ASSET_STATUSES = ["ACTIVE", "INACTIVE", "RETIRED", "MAINTENANCE"]
WORK_ORDER_TYPES = [
    "INSPECTION",
    "REPAIR",
    "INSTALLATION",
    "MAINTENANCE",
    "EMERGENCY_RESPONSE",
]
WORK_ORDER_PRIORITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
WORK_ORDER_STATUSES = ["OPEN", "IN_PROGRESS", "COMPLETED", "CANCELLED"]
METER_TYPES = ["AMI_GAS", "SMART_GAS", "LEGACY_GAS"]
METER_STATUSES = ["ACTIVE", "INACTIVE", "RETIRED", "PENDING"]
USAGE_UNITS = ["CCF", "MCF", "THERM"]

DEPARTMENT_TITLES = {
    "Operations": [
        "Operations Manager",
        "Operations Supervisor",
        "Operations Analyst",
        "Gas Operations Specialist",
    ],
    "Field Services": [
        "Field Services Manager",
        "Field Supervisor",
        "Field Technician",
        "Senior Field Technician",
    ],
    "Customer Service": [
        "Customer Service Manager",
        "Customer Service Supervisor",
        "Customer Service Representative",
        "Account Specialist",
    ],
    "Engineering": [
        "Engineering Manager",
        "Senior Gas Engineer",
        "Gas Engineer",
        "Engineering Technician",
    ],
    "Asset Management": [
        "Asset Management Manager",
        "Asset Strategy Analyst",
        "Asset Data Specialist",
        "Reliability Engineer",
    ],
    "Meter Services": [
        "Meter Services Manager",
        "Meter Services Supervisor",
        "Meter Technician",
        "Meter Data Analyst",
    ],
    "IT": [
        "IT Manager",
        "Systems Engineer",
        "Data Engineer",
        "Application Analyst",
    ],
    "Safety": [
        "Safety Manager",
        "Safety Specialist",
        "Compliance Analyst",
        "Field Safety Coordinator",
    ],
}


def require_environment():
    load_dotenv()
    required = [
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            f"Missing required environment variable(s): {', '.join(missing)}"
        )

    try:
        int(os.environ["POSTGRES_PORT"])
    except ValueError as exc:
        raise RuntimeError("POSTGRES_PORT must be a valid integer.") from exc


def connect():
    require_environment()
    return psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def weighted_choice(values, weights):
    return random.choices(values, weights=weights, k=1)[0]


def decimal_quantity(minimum, maximum):
    value = Decimal(str(random.uniform(minimum, maximum)))
    return value.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


def utc_datetime(day, hour=12):
    return datetime.combine(day, time(hour=hour), tzinfo=timezone.utc)


def clear_utility_tables(cursor):
    cursor.execute(
        """
        TRUNCATE TABLE
            utility_source.ami_meter_readings,
            utility_source.erp_work_orders,
            utility_source.ami_meters,
            utility_source.erp_assets,
            utility_source.customer_service_accounts,
            utility_source.hr_employees,
            utility_source.service_locations
        RESTART IDENTITY
        """
    )
    print("Cleared existing rows from the seven utility tables.")


def load_service_locations(cursor, run_date):
    rows = []
    service_type_weights = [75, 20, 5]
    status_weights = [88, 5, 4, 3]

    for number in range(1, NUM_SERVICE_LOCATIONS + 1):
        city, postal_code = random.choice(FLORIDA_CITIES)
        created_day = fake.date_between(
            start_date=run_date - timedelta(days=3650),
            end_date=run_date - timedelta(days=30),
        )
        updated_day = fake.date_between(start_date=created_day, end_date=run_date)
        rows.append(
            (
                f"SL-{number:06d}",
                fake.street_address(),
                fake.secondary_address() if random.random() < 0.12 else None,
                city,
                "FL",
                postal_code,
                weighted_choice(
                    ["Hillsborough", "Pinellas", "Polk", "Pasco"],
                    [50, 20, 15, 15],
                ),
                weighted_choice(SERVICE_TYPES, service_type_weights),
                weighted_choice(SERVICE_STATUSES, status_weights),
                decimal_quantity(27.70, 28.20),
                decimal_quantity(-82.80, -81.90),
                utc_datetime(created_day),
                utc_datetime(updated_day),
            )
        )

    execute_values(
        cursor,
        """
        INSERT INTO utility_source.service_locations (
            service_location_number,
            address_line_1,
            address_line_2,
            city,
            state,
            postal_code,
            county,
            service_type,
            service_status,
            latitude,
            longitude,
            created_at,
            updated_at
        ) VALUES %s
        """,
        rows,
        page_size=500,
    )
    cursor.execute(
        """
        SELECT service_location_id, service_type
        FROM utility_source.service_locations
        ORDER BY service_location_id
        """
    )
    return cursor.fetchall()


def load_customer_service_accounts(cursor, service_locations, run_date):
    rows = []
    location_types = dict(service_locations)

    for number in range(1, NUM_CUSTOMER_SERVICE_ACCOUNTS + 1):
        if number <= len(service_locations):
            service_location_id = service_locations[number - 1][0]
        else:
            service_location_id = random.choice(service_locations)[0]

        customer_type = location_types[service_location_id].removeprefix("GAS_")
        account_status = weighted_choice(
            ACCOUNT_STATUSES,
            [82, 6, 8, 4],
        )
        start_date = fake.date_between(
            start_date=run_date - timedelta(days=3650),
            end_date=run_date,
        )
        if account_status in {"CLOSED", "INACTIVE"} and random.random() < 0.85:
            end_date = fake.date_between(start_date=start_date, end_date=run_date)
        else:
            end_date = None

        if customer_type == "RESIDENTIAL":
            customer_name = fake.name()
        elif customer_type == "COMMERCIAL":
            customer_name = fake.company()
        else:
            customer_name = f"{fake.company()} Industrial"

        created_at = utc_datetime(start_date)
        rows.append(
            (
                f"CSA-{number:06d}",
                service_location_id,
                customer_name,
                customer_type,
                account_status,
                start_date,
                end_date,
                f"{random.randint(1, 20):02d}",
                created_at,
                utc_datetime(end_date or run_date),
            )
        )

    execute_values(
        cursor,
        """
        INSERT INTO utility_source.customer_service_accounts (
            customer_account_number,
            service_location_id,
            customer_name,
            customer_type,
            account_status,
            start_date,
            end_date,
            billing_cycle,
            created_at,
            updated_at
        ) VALUES %s
        """,
        rows,
        page_size=500,
    )


def load_hr_employees(cursor, run_date):
    departments = list(DEPARTMENT_TITLES)
    rows = []

    for number in range(1, NUM_HR_EMPLOYEES + 1):
        department = (
            departments[number - 1]
            if number <= len(departments)
            else random.choice(departments)
        )
        title_options = DEPARTMENT_TITLES[department]
        job_title = (
            title_options[0]
            if number <= len(departments)
            else random.choice(title_options[1:])
        )
        status = (
            "ACTIVE"
            if number <= len(departments)
            else weighted_choice(EMPLOYMENT_STATUSES, [88, 4, 5, 3])
        )
        hire_date = fake.date_between(
            start_date=run_date - timedelta(days=25 * 365),
            end_date=run_date - timedelta(days=30),
        )
        rows.append(
            (
                f"EMP-{number:06d}",
                fake.first_name(),
                fake.last_name(),
                department,
                job_title,
                status,
                hire_date,
                None,
                utc_datetime(hire_date),
                utc_datetime(run_date),
            )
        )

    execute_values(
        cursor,
        """
        INSERT INTO utility_source.hr_employees (
            employee_number,
            first_name,
            last_name,
            department,
            job_title,
            employment_status,
            hire_date,
            manager_employee_id,
            created_at,
            updated_at
        ) VALUES %s
        """,
        rows,
        page_size=500,
    )

    cursor.execute(
        """
        SELECT employee_id, department, employment_status
        FROM utility_source.hr_employees
        ORDER BY employee_id
        """
    )
    employees = cursor.fetchall()
    department_managers = {
        department: employee_id
        for employee_id, department, _status in employees[: len(departments)]
    }

    manager_updates = [
        (department_managers[department], employee_id)
        for employee_id, department, _status in employees[len(departments) :]
    ]
    execute_values(
        cursor,
        """
        UPDATE utility_source.hr_employees AS employee
        SET manager_employee_id = update_values.manager_employee_id
        FROM (VALUES %s) AS update_values(manager_employee_id, employee_id)
        WHERE employee.employee_id = update_values.employee_id
        """,
        manager_updates,
        page_size=500,
    )
    return employees


def load_erp_assets(cursor, service_locations, run_date):
    rows = []

    for number in range(1, NUM_ERP_ASSETS + 1):
        if number <= len(service_locations):
            service_location_id = service_locations[number - 1][0]
        else:
            service_location_id = random.choice(service_locations)[0]
        install_date = fake.date_between(
            start_date=run_date - timedelta(days=30 * 365),
            end_date=run_date - timedelta(days=7),
        )
        rows.append(
            (
                f"AST-{number:06d}",
                weighted_choice(ASSET_TYPES, [30, 12, 18, 12, 20, 8]),
                weighted_choice(ASSET_STATUSES, [84, 5, 5, 6]),
                install_date,
                service_location_id,
                utc_datetime(install_date),
                utc_datetime(run_date),
            )
        )

    execute_values(
        cursor,
        """
        INSERT INTO utility_source.erp_assets (
            asset_number,
            asset_type,
            asset_status,
            install_date,
            service_location_id,
            created_at,
            updated_at
        ) VALUES %s
        """,
        rows,
        page_size=500,
    )
    cursor.execute(
        "SELECT asset_id FROM utility_source.erp_assets ORDER BY asset_id"
    )
    return [row[0] for row in cursor.fetchall()]


def load_erp_work_orders(cursor, asset_ids, employees, run_date):
    active_employee_ids = [
        employee_id
        for employee_id, _department, status in employees
        if status == "ACTIVE"
    ]
    rows = []

    for number in range(1, NUM_ERP_WORK_ORDERS + 1):
        status = weighted_choice(WORK_ORDER_STATUSES, [20, 18, 55, 7])
        opened_date = fake.date_between(
            start_date=run_date - timedelta(days=730),
            end_date=run_date,
        )
        if status in {"COMPLETED", "CANCELLED"}:
            closed_date = fake.date_between(
                start_date=opened_date,
                end_date=run_date,
            )
        else:
            closed_date = None

        if status == "OPEN" and random.random() < 0.30:
            assigned_employee_id = None
        else:
            assigned_employee_id = random.choice(active_employee_ids)

        rows.append(
            (
                f"WO-{number:06d}",
                random.choice(asset_ids),
                assigned_employee_id,
                weighted_choice(WORK_ORDER_TYPES, [30, 22, 12, 30, 6]),
                weighted_choice(WORK_ORDER_PRIORITIES, [40, 35, 20, 5]),
                status,
                opened_date,
                closed_date,
                utc_datetime(opened_date),
                utc_datetime(closed_date or run_date),
            )
        )

    execute_values(
        cursor,
        """
        INSERT INTO utility_source.erp_work_orders (
            work_order_number,
            asset_id,
            assigned_employee_id,
            work_order_type,
            priority,
            status,
            opened_date,
            closed_date,
            created_at,
            updated_at
        ) VALUES %s
        """,
        rows,
        page_size=500,
    )


def load_ami_meters(cursor, service_locations, run_date):
    rows = []

    for number in range(1, NUM_AMI_METERS + 1):
        service_location_id = service_locations[(number - 1) % len(service_locations)][0]
        meter_status = weighted_choice(METER_STATUSES, [90, 4, 3, 3])
        install_date = fake.date_between(
            start_date=run_date - timedelta(days=20 * 365),
            end_date=run_date - timedelta(days=30),
        )
        last_read_date = (
            run_date
            if meter_status == "ACTIVE"
            else run_date - timedelta(days=random.randint(1, 120))
        )
        rows.append(
            (
                f"MTR-{number:06d}",
                service_location_id,
                weighted_choice(METER_TYPES, [70, 25, 5]),
                meter_status,
                install_date,
                last_read_date,
                utc_datetime(install_date),
                utc_datetime(run_date),
            )
        )

    execute_values(
        cursor,
        """
        INSERT INTO utility_source.ami_meters (
            meter_number,
            service_location_id,
            meter_type,
            meter_status,
            install_date,
            last_read_date,
            created_at,
            updated_at
        ) VALUES %s
        """,
        rows,
        page_size=500,
    )
    cursor.execute(
        """
        SELECT meter.meter_id, location.service_type
        FROM utility_source.ami_meters AS meter
        JOIN utility_source.service_locations AS location
          ON location.service_location_id = meter.service_location_id
        ORDER BY meter.meter_id
        """
    )
    meters = cursor.fetchall()
    return [(meter_id, service_type) for meter_id, service_type in meters]


def usage_range(service_type):
    if service_type == "GAS_INDUSTRIAL":
        return 60, 250
    if service_type == "GAS_COMMERCIAL":
        return 10, 120
    return 0, 35


def load_ami_meter_readings(cursor, meters, run_date):
    first_reading_date = run_date - timedelta(days=READING_DAYS - 1)
    rows = []

    for meter_id, service_type in meters:
        minimum_usage, maximum_usage = usage_range(service_type)
        usage_unit = weighted_choice(USAGE_UNITS, [80, 5, 15])

        for day_offset in range(READING_DAYS):
            reading_date = first_reading_date + timedelta(days=day_offset)
            reading_type = weighted_choice(
                ["DAILY", "ESTIMATED", "MANUAL"],
                [94, 4, 2],
            )
            read_status = weighted_choice(
                ["VALID", "ESTIMATED", "MISSING", "ERROR"],
                [94, 3, 2, 1],
            )

            if read_status in {"MISSING", "ERROR"}:
                usage_quantity = Decimal("0.000")
            else:
                usage_quantity = decimal_quantity(minimum_usage, maximum_usage)

            if reading_type == "MANUAL":
                source_system = "MANUAL_ENTRY"
            elif reading_type == "ESTIMATED" or read_status == "ESTIMATED":
                source_system = "METER_DATA_MANAGEMENT"
            else:
                source_system = weighted_choice(
                    ["AMI_HEADEND", "METER_DATA_MANAGEMENT"],
                    [90, 10],
                )

            rows.append(
                (
                    meter_id,
                    utc_datetime(reading_date),
                    usage_quantity,
                    usage_unit,
                    reading_type,
                    read_status,
                    source_system,
                    datetime.now(timezone.utc),
                )
            )

    execute_values(
        cursor,
        """
        INSERT INTO utility_source.ami_meter_readings (
            meter_id,
            reading_timestamp,
            usage_quantity,
            usage_unit,
            reading_type,
            read_status,
            source_system,
            created_at
        ) VALUES %s
        """,
        rows,
        page_size=2_000,
    )


def scalar(cursor, query):
    cursor.execute(query)
    return cursor.fetchone()[0]


def validate_loaded_data(cursor):
    expected_counts = {
        "service_locations": NUM_SERVICE_LOCATIONS,
        "customer_service_accounts": NUM_CUSTOMER_SERVICE_ACCOUNTS,
        "hr_employees": NUM_HR_EMPLOYEES,
        "erp_assets": NUM_ERP_ASSETS,
        "erp_work_orders": NUM_ERP_WORK_ORDERS,
        "ami_meters": NUM_AMI_METERS,
        "ami_meter_readings": NUM_AMI_METER_READINGS,
    }
    results = {}
    failures = []

    print("\nLoaded row counts:")
    for table_name in UTILITY_TABLES:
        count = scalar(
            cursor,
            f"SELECT COUNT(*) FROM {UTILITY_SCHEMA}.{table_name}",
        )
        results[table_name] = count
        print(f"  {table_name}: {count}")
        if count != expected_counts[table_name]:
            failures.append(
                f"{table_name} expected {expected_counts[table_name]} rows, found {count}"
            )

    validation_queries = {
        "customer_service_accounts.service_location_id orphans": """
            SELECT COUNT(*)
            FROM utility_source.customer_service_accounts AS child
            LEFT JOIN utility_source.service_locations AS parent
              ON parent.service_location_id = child.service_location_id
            WHERE parent.service_location_id IS NULL
        """,
        "erp_assets.service_location_id orphans": """
            SELECT COUNT(*)
            FROM utility_source.erp_assets AS child
            LEFT JOIN utility_source.service_locations AS parent
              ON parent.service_location_id = child.service_location_id
            WHERE parent.service_location_id IS NULL
        """,
        "erp_work_orders.asset_id orphans": """
            SELECT COUNT(*)
            FROM utility_source.erp_work_orders AS child
            LEFT JOIN utility_source.erp_assets AS parent
              ON parent.asset_id = child.asset_id
            WHERE parent.asset_id IS NULL
        """,
        "erp_work_orders.assigned_employee_id orphans": """
            SELECT COUNT(*)
            FROM utility_source.erp_work_orders AS child
            LEFT JOIN utility_source.hr_employees AS parent
              ON parent.employee_id = child.assigned_employee_id
            WHERE child.assigned_employee_id IS NOT NULL
              AND parent.employee_id IS NULL
        """,
        "ami_meters.service_location_id orphans": """
            SELECT COUNT(*)
            FROM utility_source.ami_meters AS child
            LEFT JOIN utility_source.service_locations AS parent
              ON parent.service_location_id = child.service_location_id
            WHERE parent.service_location_id IS NULL
        """,
        "ami_meter_readings.meter_id orphans": """
            SELECT COUNT(*)
            FROM utility_source.ami_meter_readings AS child
            LEFT JOIN utility_source.ami_meters AS parent
              ON parent.meter_id = child.meter_id
            WHERE parent.meter_id IS NULL
        """,
        "negative usage records": """
            SELECT COUNT(*)
            FROM utility_source.ami_meter_readings
            WHERE usage_quantity < 0
        """,
        "work orders closed before opened": """
            SELECT COUNT(*)
            FROM utility_source.erp_work_orders
            WHERE closed_date < opened_date
        """,
    }

    print("\nIntegrity validation:")
    for label, query in validation_queries.items():
        count = scalar(cursor, query)
        print(f"  {label}: {count}")
        if count != 0:
            failures.append(f"{label} expected 0, found {count}")

    cursor.execute(
        """
        SELECT
            MIN(reading_timestamp),
            MAX(reading_timestamp),
            COUNT(DISTINCT reading_timestamp::date)
        FROM utility_source.ami_meter_readings
        """
    )
    minimum_timestamp, maximum_timestamp, distinct_dates = cursor.fetchone()
    print(f"  minimum reading_timestamp: {minimum_timestamp}")
    print(f"  maximum reading_timestamp: {maximum_timestamp}")
    print(f"  distinct reading dates: {distinct_dates}")
    if distinct_dates < READING_DAYS:
        failures.append(
            f"distinct reading dates expected at least {READING_DAYS}, "
            f"found {distinct_dates}"
        )

    if failures:
        details = "\n  - ".join(failures)
        raise RuntimeError(f"Utility data validation failed:\n  - {details}")

    print("\nAll utility data validation checks passed.")
    return results


def main():
    connection = None
    cursor = None

    try:
        run_date = date.today()
        connection = connect()
        connection.autocommit = False
        cursor = connection.cursor()

        print(f"Generating utility data for run date {run_date.isoformat()}.")
        clear_utility_tables(cursor)

        service_locations = load_service_locations(cursor, run_date)
        load_customer_service_accounts(cursor, service_locations, run_date)
        employees = load_hr_employees(cursor, run_date)
        asset_ids = load_erp_assets(cursor, service_locations, run_date)
        load_erp_work_orders(cursor, asset_ids, employees, run_date)
        meters = load_ami_meters(cursor, service_locations, run_date)
        load_ami_meter_readings(cursor, meters, run_date)

        validate_loaded_data(cursor)
        connection.commit()
        print("\nSynthetic utility source data load committed successfully.")
        return 0

    except Exception as exc:
        if connection is not None:
            connection.rollback()
        print(
            f"Utility data load failed and was rolled back: {exc}",
            file=sys.stderr,
        )
        return 1

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    sys.exit(main())
