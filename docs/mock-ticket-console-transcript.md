# Captured local mock-ticket console transcript

**Observed local mock output** from this command (no model service, credential, HTTP client, or network call):

```text
uv run python main.py --offline --count 1 --no-color --ticket-adapter fake-jira

[System] OFFLINE SIMULATION
  All roles simulated; no model calls or production changes.

[Fake Jira Adapter] LOCAL MOCK ENABLED
  In-memory synthetic records only; no credential or network use.

[Incident Reporter] Report -> Incident Responder
  ID: INC-b540cfcf
  Service: inventory-api
  Summary: Every stock reservation returns an error.

[Architect] Classification and resolution plan
  Incident type: deployment_regression
  Priority: P1
  Runbook ID: RB-001
  Action: rollback

[Fake Jira Adapter] MOCK progress comment
  [SIMULATION/MOCK] Assignment recorded for role Engineer; fixture='mock-engineer-fixture'. Engineer
    is a role, not an account identifier.

[Fake Jira Adapter] MOCK ticket created
  Mock ticket: SIM-1
  Url: https://jira.example.invalid/browse/SIM-1
  Correlation ID: EXT-744f21bc702e4370a595826e601d69ed
  Simulation: Yes

[Engineer] Implementation complete (simulated)
  Success: Yes

[Fake Jira Adapter] MOCK progress comment
  [SIMULATION/MOCK] Simulated remediation reported success=True; no production action occurred.

[Tester] Validation result (simulated)
  Passed: Yes

[Fake Jira Adapter] MOCK progress comment
  [SIMULATION/MOCK] Simulated validation reported passed=True; no production validation occurred.

[Fake Jira Adapter] MOCK local lifecycle
  SIMULATED_VALIDATED_LOCAL_ONLY

[Incident Responder] INC-b540cfcf | Final status: RESOLVED
```

`INC-b540cfcf` and `EXT-744f21bc702e4370a595826e601d69ed` were random IDs from this observed **synthetic** run. `SIM-1` is a local, in-memory fake key. The last responder line is the original simulation's internal status; it is not a Jira status, Jira transition, real recovery, or production closure.

## MOCK — redacted fake Jira-shaped record (not sandbox output)

This is a deliberately redacted **MOCK** illustration of the in-memory data shape; it was not retrieved from Jira or any sandbox:

```text
MOCK ONLY / NOT JIRA CLOUD
key: SIM-1
url: https://jira.example.invalid/browse/SIM-1
correlation_id: EXT-[redacted-synthetic]
incident_id: INC-[redacted-synthetic]
project: SIM
issue_type: Incident
priority: P1
assignee_fixture: mock-engineer-fixture  # fixture, not a Jira accountId
local_lifecycle: SIMULATED_VALIDATED_LOCAL_ONLY
comments: [SIMULATION/MOCK] ... (three local records)
```
