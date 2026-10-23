# Database connection exhaustion

Incident type: database_connection_exhaustion
Runbook ID: RB-004
Priority: P1
Action: recover_connections

## When to use

Database clients fail to acquire connections and active sessions reach the configured connection limit. Profile reads or another critical database-backed workflow fail while the database host remains reachable.

## Ownership and priority

Owner: Database on-call engineer with the application owner. Priority P1 for widespread failure of the dependent critical workflow.

## Diagnostics

Inspect pool utilization, session age, transaction duration, and connection errors. Identify leaking clients or idle transactions; check CPU, storage, and locks for an underlying bottleneck.

## Prerequisites

Capture session evidence and identify session owners. Have the database owner review any proposed cancellation. Do not raise limits or terminate all sessions indiscriminately.

## Steps

1. Identify which application or session group consumes the connection budget.
2. Simulate limiting excessive new connections from the offending client.
3. With database-owner review, simulate cancelling confirmed abandoned transactions.
4. Simulate correcting the client's connection handling and restoring traffic gradually.

## Validation

- Connection usage stays below 80% of its configured limit for 10 minutes.
- Profile read and write probes complete successfully.
- No new connection-acquisition errors or unintended data changes are observed.

## Escalation

Engage the database lead immediately if sessions cannot be safely identified, recovery fails, or integrity checks indicate a data issue.

## Follow-up

Track down the connection leak and add pool saturation alerts and transaction timeouts.

## Simulation scope

All actions and checks in this demo are simulated. Thresholds are illustrative and should be adapted to real service objectives.
