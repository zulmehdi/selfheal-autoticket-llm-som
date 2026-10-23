# Expired identity gateway TLS certificate

Incident type: expired_tls_certificate
Runbook ID: RB-005
Priority: P1
Action: renew_certificate

## When to use

Sign-in connections fail TLS handshakes and the identity gateway presents an expired server certificate. Backend services may remain healthy while users cannot establish new sessions.

## Ownership and priority

Owner: Identity platform on-call engineer and certificate owner. Priority P1 because new sign-ins are blocked across the organization.

## Diagnostics

Inspect the certificate actually presented at the gateway for hostname, expiry, chain, and issuer. Check client and server clocks and renewal-job logs.

## Prerequisites

Confirm certificate ownership and the correct hostname. Use the approved certificate issuer and secret store. Keep private keys out of logs and tickets.

## Steps

1. Identify the expired gateway certificate and why automated renewal failed.
2. Simulate requesting a valid replacement certificate for the correct hostname.
3. Simulate deploying the certificate and complete chain through the approved secret workflow.
4. Reload gateway instances gradually and verify the presented certificate.

## Validation

- External TLS probes pass hostname, expiry, and trust-chain checks.
- A new test user session can authenticate.
- Existing sessions remain functional and handshake errors return to baseline.

## Escalation

Engage identity and certificate owners if issuance fails or the chain is rejected. Suspected key compromise requires the security incident process.

## Follow-up

Repair renewal automation and add expiry alerts at 30, 14, and 7 days.

## Simulation scope

All actions and checks in this demo are simulated. Thresholds are illustrative and should be adapted to real service objectives.
