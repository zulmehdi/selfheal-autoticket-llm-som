# Notification queue backlog

Incident type: message_queue_backlog
Runbook ID: RB-006
Priority: P2
Action: restore_worker_throughput

## When to use

Notification messages are delayed and queue depth or oldest-message age rises because worker throughput is below the arrival rate. There is no evidence of provider throttling or poison-message failures.

## Ownership and priority

Owner: Messaging platform and notification service on-call engineers. Priority P2 because notifications are delayed while primary transactions still succeed.

## Diagnostics

Compare arrival and processing rates, oldest-message age, worker health, retry counts, and dead-letter volume. Check provider quotas before increasing concurrency.

## Prerequisites

Confirm retries are idempotent, worker capacity is available, and downstream quotas permit scaling. Preserve queued messages; do not purge the queue.

## Steps

1. Capture queue depth, oldest-message age, arrival rate, and worker throughput.
2. Check for provider throttling or poison messages; if present, stop and request a revised plan.
3. Simulate increasing healthy worker capacity within downstream quotas.
4. Drain the backlog gradually while monitoring duplicate delivery and error rates.

## Validation

- Queue depth decreases and oldest-message age returns below 5 minutes.
- Sample notifications arrive once and within the expected delivery window.
- Dead-letter volume and downstream errors do not increase.

## Escalation

Engage messaging and provider owners if backlog still grows after 15 minutes or quota, retry, or duplicate-delivery problems appear.

## Follow-up

Review worker autoscaling, delivery latency alerts, and retry limits.

## Simulation scope

All actions and checks in this demo are simulated. Thresholds are illustrative and should be adapted to real service objectives.
