# Lab 01 — Source-System Discovery and Centralization Plan

## Answer this lab makes real

“How would you centralize scattered ERP, HR, AMI, operational, and reporting data?”

## Objective

Create a repeatable inventory of the current PostgreSQL utility sources and turn it into a phased centralization design. You should learn that centralization begins with discovery, ownership, grain, sensitivity, and quality expectations—not with immediately copying tables.

## Build

Create:

- `inventory_sources.sql` — catalog tables, columns, keys, constraints, indexes, and approximate row counts.
- `source_inventory.md` — one section per source domain: customer service, HR, ERP, work orders, meters, and AMI readings.
- `centralization_plan.md` — source → raw/Bronze → standardized/Silver → curated/Gold.

For every table, record:

- business purpose and grain;
- primary and business keys;
- source owner and proposed data steward;
- refresh cadence;
- sensitive fields;
- expected volume and growth;
- known quality risks;
- proposed ingestion mode: full, incremental, CDC, or event.

## Hands-on steps

1. Query `information_schema` and PostgreSQL catalogs.
2. Confirm the seven tables under `utility_source`.
3. Profile counts and AMI date range.
4. Draw the domain relationships.
5. Decide which data should be raw, standardized, curated, restricted, or aggregated.
6. Define a phased implementation order and explain the dependencies.
7. Add one small JSON document representing a NoSQL meter/device event. Document how its nested structure would be profiled, landed unchanged in Bronze, and flattened for analytical use.

## Deliberate challenge

Assume the HR owner and AMI owner define “active” differently. Document how you would resolve the definition conflict before publishing a shared metric.

## Evidence

- Source inventory query output
- Domain relationship diagram
- Centralization architecture
- Source onboarding checklist
- NoSQL/document-source onboarding note

## Enterprise debrief

Explain your approach in five phases: discovery, ingestion, standardization/modeling, governance/security, and production operations. Identify where business owners, architects, security, vendors, and data stewards participate.

## Completion criteria

- All seven source tables are inventoried.
- Ownership, grain, sensitivity, and ingestion approach are explicit.
- The plan includes quality, lineage, RBAC, incremental loads, monitoring, and recovery.
