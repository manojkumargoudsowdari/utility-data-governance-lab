# Lab 02 Observations

## Objective

Lab 02 converted normalized utility source tables into a curated analytical model using dimensions and facts.

The practical goal was to move from this question:

> What source data do we have?

to this question:

> How should the data be modeled so business users can analyze usage, assets, work orders, employees, and service locations correctly?

## Source relationship summary

The source-system relationship skeleton is:

```text
service_locations
 ├── customer_service_accounts
 ├── ami_meters
 │    └── ami_meter_readings
 └── erp_assets
      └── erp_work_orders
           └── hr_employees assigned to work order

hr_employees
 └── hr_employees manager relationship
```

The most central business entity is `service_locations` because meters, customer service accounts, and assets all connect to it.

## Source grain

| Source table | Grain |
|---|---|
| `service_locations` | One row per service location |
| `customer_service_accounts` | One row per customer service account |
| `ami_meters` | One row per physical meter |
| `ami_meter_readings` | One row per meter reading timestamp |
| `erp_assets` | One row per utility asset |
| `erp_work_orders` | One row per work order |
| `hr_employees` | One row per employee |

## Curated model

The curated model was created in schema `utility_curated`.

| Curated table | Source table | Model type | Grain |
|---|---|---|---|
| `dim_service_location` | `service_locations` | Dimension | One row per service location |
| `dim_meter` | `ami_meters` | Dimension | One row per meter |
| `dim_asset` | `erp_assets` | Dimension | One row per asset |
| `dim_employee` | `hr_employees` | Dimension | One row per employee |
| `fact_meter_usage_daily` | `ami_meter_readings` | Fact | One row per meter per reading date |
| `fact_work_order` | `erp_work_orders` | Fact | One row per work order |

## Why dimensions and facts were separated

Dimensions describe business entities:

- Service locations
- Meters
- Assets
- Employees

Facts record measurable events or operational activity:

- AMI usage readings
- Work orders

This structure makes reporting easier because business users can analyze measures such as usage quantity, work-order count, open work orders, completed work orders, and days to close by dimensions such as city, service location, asset type, meter, employee, department, priority, and status.

## AMI daily usage fact

The source AMI table stores reading-level data.

Source grain:

> One row per meter reading timestamp.

Curated fact grain:

> One row per meter per reading date.

The daily fact aggregates usage using:

```sql
SUM(usage_quantity)
```

This makes the table easier for daily reporting while preserving the total source usage.

## Work-order fact

The work-order fact captures utility field and asset-maintenance activity.

Fact grain:

> One row per work order.

Useful measures and indicators include:

- Work-order count
- Completed work-order count
- Open work-order count
- High-priority or critical-priority count
- Days to close
- Average days to close

The fact can be analyzed by:

- Asset
- Service location
- City
- Assigned employee
- Department
- Work-order type
- Priority
- Status
- Opened date

## Validation results

### Curated row counts

| Curated table | Row count |
|---|---:|
| `dim_asset` | 800 |
| `dim_employee` | 120 |
| `dim_meter` | 1,000 |
| `dim_service_location` | 500 |
| `fact_meter_usage_daily` | 30,000 |
| `fact_work_order` | 600 |

### Dimension business-key uniqueness

| Check | Duplicate count |
|---|---:|
| `dim_service_location.service_location_number` | 0 |
| `dim_meter.meter_number` | 0 |
| `dim_asset.asset_number` | 0 |
| `dim_employee.employee_number` | 0 |

### Fact grain validation

`fact_meter_usage_daily` returned no duplicate rows for:

```text
meter_key + reading_date
```

This confirms:

> One row per meter per reading date.

`fact_work_order` returned no duplicate rows for:

```text
work_order_id
```

This confirms:

> One row per work order.

### AMI usage reconciliation

| Total source usage | Total curated usage | Difference |
|---:|---:|---:|
| 982,691.232 | 982,691.232 | 0.000 |

The curated daily usage fact preserved the source usage total.

### Work-order count reconciliation

| Source work orders | Curated work orders | Difference |
|---:|---:|---:|
| 600 | 600 | 0 |

The curated work-order fact preserved the source work-order count.

### Required dimension context

| Check | Result |
|---|---:|
| Work orders missing required asset or service-location context | 0 |

Every curated work order has valid required asset and service-location context.

## Production analogy

In production, this lab maps to creating curated warehouse or lakehouse tables from operational systems.

For example:

- ERP asset data becomes an asset dimension.
- HR employee data becomes an employee dimension.
- AMI interval or daily readings become a usage fact.
- Work-order events become an operational work-order fact.
- Service locations become a shared conformed dimension used across usage, assets, accounts, and operations.

In Snowflake or Databricks, these objects might live in curated schemas or gold-layer tables. The same modeling logic applies even though this lab uses PostgreSQL locally.

## Enterprise takeaway

> I designed a curated utility data model by separating descriptive entities into dimensions and measurable operational activity into facts. I defined the grain of each source and target table, mapped source systems into dimensions and facts, aggregated AMI readings into a daily meter usage fact, and modeled work orders as one row per work order. I validated the model through row-count reconciliation, business-key uniqueness checks, fact-grain checks, usage-total reconciliation, and required relationship checks.
