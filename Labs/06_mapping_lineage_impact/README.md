# Lab 06 — Source-to-Target Mapping, Lineage, and Impact Analysis

## Answers this lab makes real

- “Explain source-to-target mapping and data lineage.”
- “How do you collaborate across business and technical teams?”

## Objective

Trace selected utility data from PostgreSQL source columns through raw, standardized, curated, and reporting assets, then use the lineage to perform impact analysis.

## Build

Create:

- `utility_source_to_target_mapping.yml`
- `utility_lineage.yml`
- `impact_analysis.md`
- `lineage_validation.py`

Map at least:

- `ami_meter_readings.usage_quantity` → daily usage fact → city usage mart
- `erp_work_orders.status` → work-order fact → status summary
- `hr_employees.department` → employee dimension → productivity mart
- `service_locations.city` → location dimension → business-development report

For every mapping, capture source/target type, transformation, join, filter, key, quality rule, owner, steward, and consumer.

## Deliberate change

Assume `usage_unit` gains a new value or `work_order.status` is renamed. Use lineage to identify every affected pipeline, model, test, report, access rule, and owner.

## Evidence

- Column mappings
- End-to-end lineage
- Impact report
- Stakeholder/RACI list
- Required test plan

## Enterprise debrief

Explain that mapping is the transformation contract and lineage is the end-to-end dependency graph. Demonstrate how both support development, validation, troubleshooting, governance, audit, and communication.

## Completion criteria

- Selected fields are traceable source-to-report.
- Every impacted object is identified for the deliberate change.
- Business and technical ownership are explicit.

