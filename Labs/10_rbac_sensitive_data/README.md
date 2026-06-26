# Lab 10 — RBAC and Sensitive Utility Data

## Answer this lab makes real

“How do you secure HR, customer, and AMI usage data?”

## Objective

Implement and test least-privilege PostgreSQL roles and protected views for different business personas.

## Build

Create:

- `create_roles.sql`
- `create_secure_views.sql`
- `grant_access.sql`
- `test_access.sql`
- `access_matrix.md`
- `access_review.md`

## Personas

- Data Engineer
- Data Steward
- HR Analyst
- Operations Analyst
- Executive Reporting User
- AI/ML Consumer
- Auditor

## Controls

- Restrict direct HR and customer table access.
- Mask employee/customer identifiers where appropriate.
- Give executives aggregates instead of meter-level usage.
- Give auditors read-only governance/evidence access.
- Separate object ownership from consumer roles.
- Test inherited roles and revoked access.

## Deliberate failures

- Operations role selects detailed HR data.
- Executive role selects raw AMI readings.
- Read-only role attempts an update.
- Revoked role reconnects and attempts access.

## Evidence

- Access matrix
- Role hierarchy
- Successful authorized queries
- Permission-denied results
- Masked-view output
- Recertification checklist

## Enterprise debrief

Explain classification, business-role design, least privilege, schema/table/view/column controls, masking, aggregate access, approval workflow, audit logging, and periodic access review.

## Completion criteria

- Authorized work succeeds.
- Unauthorized work fails.
- Sensitive values are masked or inaccessible.
- No credentials are committed.

