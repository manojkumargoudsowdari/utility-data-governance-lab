# Lab 02 — Logical and Physical Utility Data Modeling

## Answers this lab makes real

- “Explain a data model you designed.”
- “What is AMI data, and how would you model it?”

## Objective

Translate operational utility tables into a documented analytical model with explicit grain, keys, dimensions, facts, and history.

## Build

Create:

- `source_model.md` — normalized operational model.
- `curated_model.md` — proposed dimensions and facts.
- `model_ddl.sql` — local reporting schema and model DDL.
- `model_validation.sql` — uniqueness, grain, and relationship checks.

Design:

- `dim_service_location`
- `dim_service_account`
- `dim_meter`
- `dim_asset`
- `dim_employee`
- `fact_meter_usage_daily`
- `fact_work_order`
- one historical model, such as meter-to-location or asset-status history

## Hands-on steps

1. State the grain of every source and target table before writing SQL.
2. Identify surrogate keys, business keys, foreign keys, attributes, and measures.
3. Aggregate readings to one meter per reading date.
4. Join work orders to asset, employee, and location context.
5. Choose and implement one slowly changing dimension strategy.
6. Validate unique dimension keys and fact grains.

## Deliberate challenge

Move a meter from one service location to another. Show how the model preserves historical readings at the original location while new readings use the new location.

## Evidence

- Logical and physical diagrams
- Grain matrix
- DDL
- Validation results
- Example historical record

## Enterprise debrief

Explain the business problem, model grain, keys, relationships, measures, history strategy, and why business users should consume curated models instead of operational joins.

## Completion criteria

- Every model has an unambiguous grain.
- Business keys are unique where required.
- Daily usage reconciles to source readings.
- Historical changes do not rewrite prior business context.
