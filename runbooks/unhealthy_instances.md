# Unhealthy service instances

Incident type: unhealthy_instances
Runbook ID: RB-002
Priority: P2
Action: restart

## When to use

Some service instances fail health probes without a recent deployment; remaining instances serve requests. Example: intermittent product-search timeouts with a healthy search index.

## Ownership and priority

Owner: Platform on-call engineer and service owner. Priority P2 because only a subset of requests is affected.

## Diagnostics

Compare failing and healthy instances, resource pressure, probe failures, and network reachability. Verify the data store or search index is healthy before restarting.

## Prerequisites

Confirm sufficient healthy capacity and drain connections before replacing an instance. Preserve logs and avoid restarting the whole fleet together.

## Steps

1. Identify failing instances and capture health probe output and resource metrics.
2. Drain one unhealthy instance from traffic.
3. Simulate restarting or replacing that instance and wait for readiness.
4. Repeat one instance at a time only if healthy capacity remains sufficient.

## Validation

- All replacement instances pass readiness probes.
- Search queries return expected results without timeouts.
- Error rate and latency remain at baseline for 10 minutes.

## Escalation

If failures recur after one replacement or healthy capacity falls below the service minimum, stop replacements and engage the platform lead.

## Follow-up

Investigate resource leaks or node failures and improve health-probe alerts.

## Simulation scope

All actions and checks in this demo are simulated. Thresholds are illustrative and should be adapted to real service objectives.
