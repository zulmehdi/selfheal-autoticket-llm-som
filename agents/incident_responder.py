"""Incident responder: forward incoming reports and coordinate simulation only."""

import json
from uuid import uuid4

from libs.console import emit
from libs.jira_client import (
    AmbiguousFakeCreateTimeout,
    FakeTicketCreateError,
    FakeTicketRequest,
    TicketAdapter,
)


REPORT_FIELDS = ("id", "service", "summary", "impact", "evidence")


def validate_incident(incident):
    """Accept observational reports before classification or optional mock ticketing."""
    if not isinstance(incident, dict) or any(
        not isinstance(incident.get(field), str) or not incident[field].strip()
        for field in REPORT_FIELDS
    ):
        raise ValueError("Incident responder requires nonempty id, service, summary, impact, and evidence strings")


class IncidentResponder:
    """The responder narrates with an LLM; Python enforces the handoff order."""

    def __init__(self, model, ticket_adapter: TicketAdapter | None = None):
        self.model = model
        self.ticket_adapter = ticket_adapter

    def report(self, instruction, context):
        if self.model is None:
            return instruction + " [offline simulation]"
        response = self.model.invoke([
            ("system", "You are an incident responder in a simulation. Give a brief update "
             "using only supplied facts. Follow the architect's priority and steps. "
             "Engineering and testing results are simulated, not real production actions."),
            ("human", instruction + "\n" + json.dumps(context)),
        ])
        return response.content

    def _create_mock_ticket(self, incident, plan):
        """Create only after report acceptance and architect runbook classification."""
        adapter = self.ticket_adapter
        if adapter is None:
            return None
        correlation_id = f"EXT-{uuid4().hex}"  # persisted in the local ticket request before create
        request = FakeTicketRequest(
            correlation_id=correlation_id,
            incident_id=incident["id"],
            service=incident["service"],
            summary=incident["summary"],
            impact=incident["impact"],
            evidence=incident["evidence"],
            incident_category=plan["incident_type"],
            priority=plan["priority"],
            runbook_id=plan["runbook_id"],
            planned_steps=tuple(plan["steps"]),
        )
        try:
            ticket = adapter.create_ticket(request)
        except AmbiguousFakeCreateTimeout:
            ticket = adapter.find_by_correlation(correlation_id)
            if ticket is None:
                raise RuntimeError("Local mock timeout could not reconcile correlation")
            emit("Fake Jira Adapter", "MOCK create timeout reconciled", {
                "mock_ticket": ticket.key, "correlation_id": correlation_id,
                "note": "local in-memory record found; no network request was made",
            })
        except FakeTicketCreateError:
            raise
        assignment_comment = adapter.add_progress_comment(
            ticket.key,
            f"Assignment recorded for role Engineer; fixture={ticket.request.assignee_fixture!r}. "
            "Engineer is a role, not an account identifier.",
        )
        emit("Fake Jira Adapter", "MOCK progress comment", assignment_comment.body)
        emit("Fake Jira Adapter", "MOCK ticket created", {
            "mock_ticket": ticket.key, "url": ticket.url, "correlation_id": correlation_id,
            "simulation": True,
        })
        return ticket

    def resolve(self, incident, architect, engineer, tester):
        validate_incident(incident)
        emit("Incident Responder", f"Received {incident['id']}", incident["summary"])
        emit("Incident Responder", "Consulting -> Architect", "Requesting incident type, priority, and runbook action.")
        plan = architect.decide(incident)
        emit("Architect", "Classification and resolution plan", plan)

        mock_ticket = self._create_mock_ticket(incident, plan)
        ticket = {"incident": incident, "plan": plan, "assignee": "Engineer", "status": "assigned"}
        emit("Incident Responder", "Assignment -> Engineer", self.report(
            "Explain the architect's plan and assignment to the engineer.", ticket))

        fix = engineer.implement(ticket)
        emit("Engineer", "Implementation complete (simulated)", fix)
        if mock_ticket is not None and self.ticket_adapter is not None:
            remediation_comment = self.ticket_adapter.add_progress_comment(
                mock_ticket.key,
                f"Simulated remediation reported success={fix['success']}; no production action occurred.",
            )
            emit("Fake Jira Adapter", "MOCK progress comment", remediation_comment.body)
        ticket["status"] = "awaiting_validation"
        emit("Incident Responder", "Validation request -> Tester", "Validate the simulated fix.")
        validation = tester.validate(ticket, fix)
        emit("Tester", "Validation result (simulated)", validation)
        if mock_ticket is not None and self.ticket_adapter is not None:
            validation_comment = self.ticket_adapter.add_progress_comment(
                mock_ticket.key,
                f"Simulated validation reported passed={validation['passed']}; no production validation occurred.",
            )
            emit("Fake Jira Adapter", "MOCK progress comment", validation_comment.body)

        ticket["status"] = "resolved" if fix["success"] and validation["passed"] else "needs_follow_up"
        if mock_ticket is not None and self.ticket_adapter is not None:
            lifecycle = (
                "SIMULATED_VALIDATED_LOCAL_ONLY"
                if ticket["status"] == "resolved"
                else "SIMULATED_NEEDS_FOLLOW_UP"
            )
            self.ticket_adapter.set_local_lifecycle(mock_ticket.key, lifecycle)
            emit("Fake Jira Adapter", "MOCK local lifecycle", lifecycle)
        result = {"ticket": ticket, "fix": fix, "validation": validation, "mock_ticket": mock_ticket}
        emit("Incident Responder", "Resolution update", self.report(
            "Summarize the final ticket status and the simulated validation evidence.", result))
        emit("Incident Responder", f"{incident['id']} | Final status: {ticket['status'].upper()}")
        return result
