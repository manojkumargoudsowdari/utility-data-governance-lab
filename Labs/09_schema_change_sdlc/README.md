# Lab 09 — Schema and DDL Change Through SDLC

## Answer this lab makes real

“How do you handle schema or DDL changes in production?”

## Objective

Implement a realistic source/model change through discovery, impact analysis, DEV/UAT testing, deployment, rollback, documentation, and post-deployment validation.

## Change scenario

Add a nullable `cost_center` to HR employees and a new controlled meter status or reading attribute. Then evaluate a breaking datatype change separately.

## Build

Create:

- `migration_up.sql`
- `migration_down.sql`
- `impact_analysis.md`
- `regression_tests.sql`
- `release_plan.md`
- `change_record.md`

## Hands-on steps

1. Confirm business reason and owner approval.
2. Use Lab 06 lineage for impact.
3. Update DDL, generator, mappings, quality rules, and affected models.
4. Test backward compatibility.
5. Validate in a separate database or schema.
6. Compare counts, aggregates, schemas, and sample records.
7. Execute release and rollback rehearsal.
8. Perform post-deployment checks.

## Deliberate failure

Attempt a breaking change without updating a dependent transformation. Capture the failure, rollback, and missing impact item.

## Evidence

- Up/down migration
- Impacted-object list
- Regression output
- Approval and release checklist
- Rollback evidence
- Updated lineage/change history

## Enterprise debrief

Explain requirement confirmation, impact analysis, backward compatibility, DEV/UAT testing, approvals, rollback planning, production monitoring, and audit-ready documentation.

## Completion criteria

- Compatible change succeeds without breaking consumers.
- Breaking change is caught before production.
- Rollback is tested.
- Documentation and lineage are updated.

