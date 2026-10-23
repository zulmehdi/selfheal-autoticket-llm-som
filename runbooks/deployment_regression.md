# Service failure after deployment

Incident type: deployment_regression
Runbook ID: RB-001
Priority: P1
Action: rollback

## When to use

Errors begin immediately after a deployment, the previous release was healthy, and a critical service is unavailable. Apply to any affected application, such as inventory-api.

## Ownership and priority

Owner: Application on-call engineer. Priority P1 because a critical workflow is unavailable to all users.

## Diagnostics

Compare the error timeline to release events. Check traces, dependency health, and the last known healthy deployment. Distinguish application failures from database or network outages.

## Prerequisites

Confirm the previous artifact is available and schema changes are backward compatible. Record the current release and incident evidence before changing anything.

## Steps

1. Pause further deployments to the affected service.
2. Check migration compatibility and select the last verified healthy release from deployment history.
3. Simulate rolling back the affected service to that release.
4. Wait for instances to become healthy and monitor the failing workflow.

## Validation

- Affected service health checks pass.
- Representative business transactions succeed.
- Error rate returns to its pre-incident baseline for 10 minutes.

## Escalation

If rollback is incompatible or errors persist for 10 minutes, engage the service owner and incident commander. Avoid repeated rollbacks without new evidence.

## Follow-up

Record release IDs and the defect signature. Add regression coverage before redeploying.

## Simulation scope

All actions and checks in this demo are simulated. Thresholds are illustrative and should be adapted to real service objectives.
