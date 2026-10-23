# Multi-agent incident simulation

A small incident-response demo using **Gemma in LM Studio through LiteLLM** for
reporting and coordination, and **System One / Jev** for classification.
Synthetic incidents span inventory, search, analytics, databases, identity, and
notifications. Engineering changes and validation results are always simulated.

## Quick start

Run commands from the repository root. The project targets **Python 3.14+** and
uses **uv** for dependency management.

Try all six scenarios without model services or API keys:

```powershell
python main.py --offline --count 6
```

Offline mode uses only the Python standard library, fixed observational reports,
and a simple rule-based architect stand-in. It demonstrates the handoffs rather
than model reasoning. Ticket IDs are random; classifications do not depend on IDs.

## Run with models

1. Install the project dependencies:

   ```powershell
   uv sync
   ```

2. Load `google/gemma-4-e4b` in LM Studio and start its local server.
3. Create a `.env` file in the repository root:

   ```dotenv
   LM_STUDIO_BASE_URL=http://localhost:1234/v1
   LM_STUDIO_MODEL=google/gemma-4-e4b
   LM_STUDIO_API_KEY=lm-studio
   TYPESAFE_API_KEY=your-typesafe-key
   # Optional: TYPESAFE_BASE_URL=https://your-compatible-endpoint
   ```

   Replace `lm-studio` with your server token if authentication is enabled.
   `LM_STUDIO_MODEL` is the model identifier without LiteLLM's `openai/` prefix.
   The architect requires a working TypeSafe endpoint in addition to LM Studio.

4. Start a simulation:

   ```powershell
   uv run python main.py
   uv run python main.py --count 6
   ```

By default, one report is generated. Model mode shuffles six broad scenario
prompts each run, so it does not always start with a deployment failure.
`--count 6` uses each scenario prompt once; longer runs cycle through them.
The reporter invents the details, so classifications can vary.

To supply your own premise:

```powershell
uv run python main.py --count 1 --scenario "Employees cannot sign in; the identity gateway reports TLS handshake failures."
```

The reporter sees only the premise and its reporting instructions. It has no
access to the runbooks. Its output must contain service, summary, impact, and
evidence; extra fields are discarded and Python assigns the ticket ID.

## Workflow

```text
Incident Reporter -> Incident Responder -> Architect
                            |
                     Engineer implements
                            |
                       Tester validates
                            |
                   Responder closes ticket
```

| Role | Implementation | Responsibility |
| --- | --- | --- |
| Incident Reporter | LLM, temperature 0.8 | Generate observational reports without prescribing a category, priority, or fix. |
| Incident Responder | LLM, temperature 0 | Forward reports, explain assignments, and summarize resolution. |
| Architect | System One / Jev | Classify symptoms using its loaded runbook catalog and return the matching plan. |
| Engineer | Static Python response | Always report a successful simulated implementation. |
| Tester | Static Python response | Always report passing simulated checks from the selected runbook. |

Reporter and responder use separate prompts but can share the same local model.
Python controls the handoff order. The architect loads Markdown runbooks once at
startup and sends the catalog as context on each classification request; it is
not trained on the files and does not acquire permanent model memory.

The architect chooses the incident type by meaning, not by an exact name match.
Priority, action, and steps come from the selected runbook so they stay consistent.
There is no separate dynamic severity calculation. Unknown incidents use the
fallback triage runbook. Service errors and invalid generated reports propagate
rather than silently switching to offline responses.

## Command-line options

| Option | Default | Behavior |
| --- | --- | --- |
| `--count N` | `1` | Generate and process N reports; N must be at least 1. |
| `--scenario TEXT` | Built-in scenario prompts | Use a custom premise for each report; model mode only. |
| `--offline` | Off | Use fixed reports and rule-based classification without network calls. |
| `--no-color` | Off | Disable terminal colors. |
| `--help` | | Show command-line help. |

## Console output

Each response starts with a colored `[Agent Name]` header. Fields are labelled,
runbook steps are numbered, and a final summary shows each incident's category,
priority, action, and status.

| Agent | Color |
| --- | --- |
| Incident Reporter | Cyan |
| Incident Responder | Blue |
| Architect | Magenta |
| Engineer | Yellow |
| Tester | Green |
| System | Gray |

Colors are enabled in interactive terminals and disabled for redirected output.
`--no-color` or the `NO_COLOR` environment variable disables them; `FORCE_COLOR=1`
enables them for output-capturing tools. No extra display package is required.

Example summary (ticket IDs vary):

```text
[System] FINAL SUMMARY
  INC-a1b2c3d4: database_connection_exhaustion | P1 | recover_connections | RESOLVED
  INC-e5f6a7b8: message_queue_backlog | P2 | restore_worker_throughput | RESOLVED
```

## Incident coverage and runbooks

| Example service / issue | Incident type | Priority | Runbook |
| --- | --- | --- | --- |
| Inventory failure after a release | deployment_regression | P1 | [RB-001](runbooks/deployment_regression.md) |
| Search nodes failing health probes | unhealthy_instances | P2 | [RB-002](runbooks/unhealthy_instances.md) |
| Analytics warnings without data loss | unexplained_warning | P3 | [RB-003](runbooks/unexplained_warning.md) |
| Database connection pool exhausted | database_connection_exhaustion | P1 | [RB-004](runbooks/database_connection_exhaustion.md) |
| Expired identity gateway certificate | expired_tls_certificate | P1 | [RB-005](runbooks/expired_tls_certificate.md) |
| Delayed notification delivery | message_queue_backlog | P2 | [RB-006](runbooks/message_queue_backlog.md) |
| Unrecognized or insufficient evidence | unknown | P2 | [RB-TRIAGE](runbooks/unknown.md) |

Each document contains ownership and priority rationale, diagnostics,
prerequisites, recovery steps, validation checks, escalation guidance, and
follow-up work. Thresholds are illustrative demo values. Guidance is supplied to
the architect and included in its plan; escalation instructions are not executed
automatically, and static agents do not perform real remediation or validation.

### Add or edit a runbook

Create one `.md` file per type in `runbooks/`. Use a unique incident type and
runbook ID. Restart the application after editing documents.

```markdown
# Runbook title

Incident type: unique_type_name
Runbook ID: RB-007
Priority: P2
Action: investigate

## When to use

Symptoms and evidence that distinguish this incident from other types.

## Ownership and priority

Responsible team and why this priority applies.

## Diagnostics

Metrics, logs, and dependencies to inspect.

## Prerequisites

Conditions to verify before beginning recovery.

## Steps

1. First recovery action.
2. Next recovery action.

## Validation

- A representative service-specific user journey succeeds.
- Error and latency metrics return to baseline.

## Escalation

Who to contact and when the plan should be reconsidered.

## Follow-up

Preventive changes and evidence to record.
```

The four metadata fields, `When to use` text, and numbered `Steps` are required.
Each step must be on its own line. Additional sections are preserved in the
architect's context and plan; bullet items under `Validation` become the tester's
simulated checklist. Duplicate types, malformed documents, and a missing `unknown`
fallback cause an error. Runbook paths resolve relative to the code, independent
of the terminal's working directory.

To extend the generated examples, edit `SCENARIOS` in
[agents/incident_reporter.py](agents/incident_reporter.py). For offline coverage,
also add an observational fixture to `OFFLINE_REPORTS` and a matching rule to
`DemoArchitect` in [agents/architect.py](agents/architect.py). Model mode discovers
new categories from the runbooks without an additional routing rule.

## Project layout

```text
main.py                       CLI, model setup, and simulation loop
agents/
  incident_reporter.py        LLM reporting and offline report fixtures
  incident_responder.py       Handoffs, assignment, and resolution updates
  architect.py                System One classification and offline stand-in
  engineer.py                 Static implementation response
  tester.py                   Static validation response
libs/
  console.py                  Colored, labelled terminal output
  runbook_loader.py           Markdown retrieval, parsing, and validation
runbooks/                     Individual Markdown documents and fallback triage
pyproject.toml                Python requirements and dependencies
uv.lock                       Dependency lockfile
```

## Local configuration and Git

`.env` and local variants such as `.env.local` are ignored by Git, along with
virtual environments, Python/tool caches, logs, coverage files, and editor files.
Shareable `.env.example`, `.env.sample`, and `.env.template` files are allowed;
include placeholders rather than credentials if you create one.

Keep source code, runbooks, `pyproject.toml`, `uv.lock`, and `.python-version`
versioned so other developers can reproduce the project setup.

## Mock-ticket tutorial extension (local only)

The baseline workflow above remains the default. This branch adds an **opt-in**,
stdlib-only `FakeJiraAdapter` for a runnable tutorial companion. It has local
in-memory records only, emits synthetic keys such as `SIM-1`, and uses
`https://jira.example.invalid/...`; it reads no Jira credential and makes no
network request. It is not a Jira Cloud adapter and it does not create, update,
transition, resolve, or close Jira issues. The original internal simulation
status remains separate from the mock ticket's explicitly named local lifecycle.
A successful static Engineer/Tester path means only
`SIMULATED_VALIDATED_LOCAL_ONLY`, not recovery, a Jira workflow transition, or a
production closure.

```powershell
# Existing baseline: unchanged and has no external effect.
uv run python main.py --offline --count 6 --no-color

# Opt-in local mock record; fake mode uses no credential.
uv run python main.py --offline --count 1 --no-color --ticket-adapter fake-jira

# Safe deterministic teaching paths. These never contact Jira.
uv run python main.py --offline --ticket-adapter fake-jira --fake-ticket-failure validation
uv run python main.py --offline --ticket-adapter fake-jira --fake-ticket-failure create
uv run python main.py --offline --ticket-adapter fake-jira --fake-ticket-failure create-timeout
uv run python main.py --offline --ticket-adapter fake-jira --fake-ticket-failure engineer
uv run python main.py --offline --ticket-adapter fake-jira --fake-ticket-failure tester
uv run python main.py --offline --ticket-adapter fake-jira --fake-ticket-failure unknown
```

The responder validates a report, calls `architect.decide`, then generates a
stable external correlation ID before creating a fake ticket. The ticket retains
incident ID, observations, impact, runbook category/priority/steps, and the
simulation marker. `Engineer` remains a workflow role: the optional deterministic
fixture is explicitly a fake assignee value, never an account ID. The mock stores
assignment, remediation, and validation comments locally. An injected ambiguous
create timeout reconciles that same in-memory ticket by correlation, so it does
not add a duplicate.

System One's typed `Choice` reports a selected category plus confidence in model
mode. It is a structured classification signal, not proof that the category,
plan, or any simulated outcome is correct.

See `docs/mock-ticket-console-transcript.md`,
`docs/incident-workflow-architecture.html`, and `docs/verification.md` for the
captured local evidence and scope boundary.

### Future Jira Cloud boundary — documentation only

There is intentionally no live implementation in this repository. A future,
separately reviewed Jira Cloud integration should first obtain project issue-type
metadata with `GET /rest/api/3/issue/createmeta/{projectIdOrKey}/issuetypes`,
then its fields with
`GET /rest/api/3/issue/createmeta/{projectIdOrKey}/issuetypes/{issueTypeId}`;
do not use the deprecated broad createmeta guidance. It would create with
`POST /rest/api/3/issue`, derive fields and allowed priority from that metadata,
and encode descriptions/comments as ADF. An assignee requires an `accountId`.
It would discover transition IDs at `GET .../transitions` before applying a
returned transition ID; a 201 create yields `id`, `key`, and `self`.

For a future ambiguous create timeout, persist correlation first and reconcile
only through an administrator-configured JQL-searchable correlation field or a
verified target-specific method. An issue property alone has no generally
documented property-search endpoint; this is not generic idempotency. Basic
email plus API token is appropriate only for a simple script; a distributable
integration should use OAuth 2.0 (3LO). These future notes do **not** authorize
or implement endpoints, credentials, or network traffic here.

Primary references: [issues](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/), [comments](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/), [ADF](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/), [rate limiting](https://developer.atlassian.com/cloud/jira/platform/rate-limiting/), [issue properties](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-properties/), [issue search](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/), [basic auth](https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/), and [OAuth 2.0 (3LO)](https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/).
