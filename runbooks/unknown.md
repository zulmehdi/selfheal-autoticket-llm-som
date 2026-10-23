# Unknown incident triage

Incident type: unknown
Runbook ID: RB-TRIAGE
Priority: P2
Action: investigate

## When to use

Evidence does not fit a known incident type or is insufficient to safely select a specialized runbook.

## Ownership and priority

Owner: Incident responder and relevant service on-call engineer. Priority P2 is provisional until the impact and failure are understood.

## Diagnostics

Establish affected services, first occurrence, user impact, scope, and recent changes. Gather logs, metrics, traces, and dependency health without assuming a root cause.

## Prerequisites

Preserve evidence and avoid speculative disruptive changes. Record what is observed separately from hypotheses.

## Steps

1. Collect the incident timeline, symptoms, and affected user journeys.
2. Inspect service and dependency health and compare against baseline.
3. Ask the service owner for missing evidence and classify again when the picture is clearer.
4. Simulate only a reviewed targeted fix, then verify recovery with the affected service owner.

## Validation

- The originally reported symptoms no longer occur.
- Representative service-specific user journeys pass.
- Metrics remain stable and the service owner confirms recovery.

## Escalation

Page the incident commander immediately for widespread outage, suspected security impact, or data loss. Escalate if ownership or diagnosis remains unclear after 15 minutes.

## Follow-up

Write a new runbook for the confirmed failure mode and record the incident timeline.

## Simulation scope

All actions and checks in this demo are simulated. Thresholds are illustrative and should be adapted to real service objectives.
