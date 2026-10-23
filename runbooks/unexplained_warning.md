# Non-impacting application warnings

Incident type: unexplained_warning
Runbook ID: RB-003
Priority: P3
Action: investigate

## When to use

New warning messages appear without customer impact, failed health checks, dropped data, or degraded latency. Example: parser warnings in analytics-ingestion while dashboards remain fresh.

## Ownership and priority

Owner: Application or data pipeline owner. Priority P3 because service objectives are currently met.

## Diagnostics

Collect representative warning samples and correlate them with input types, configuration, data volume, and recent changes. Check for silent data loss before assuming the warning is harmless.

## Prerequisites

Preserve sample logs with sensitive fields removed. Confirm baseline event counts and freshness. Do not suppress the warning before its cause is understood.

## Steps

1. Collect warning samples, frequency, and affected input details.
2. Compare processed and received record counts and inspect downstream freshness.
3. Identify the cause and simulate a targeted configuration or code correction.
4. Monitor the warning rate and data quality after the correction.

## Validation

- Expected event counts reconcile without missing records.
- Dashboard freshness remains within its normal objective.
- The warning stops or is documented as an understood benign condition.

## Escalation

Escalate to incident triage immediately if records are lost, freshness degrades, or customer impact appears; the P3 assumption no longer holds.

## Follow-up

Document the warning signature and add a data-quality or log regression check.

## Simulation scope

All actions and checks in this demo are simulated. Thresholds are illustrative and should be adapted to real service objectives.
