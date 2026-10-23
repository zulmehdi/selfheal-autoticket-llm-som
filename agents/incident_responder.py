"""Incident responder: forward incoming reports and coordinate resolution."""

import json

from libs.console import emit


class IncidentResponder:
    """The responder narrates with an LLM; Python enforces the handoff order."""

    def __init__(self, model):
        self.model = model

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

    def resolve(self, incident, architect, engineer, tester):
        emit("Incident Responder", f"Received {incident['id']}", incident["summary"])
        emit("Incident Responder", "Consulting -> Architect", "Requesting incident type, priority, and runbook action.")
        plan = architect.decide(incident)
        emit("Architect", "Classification and resolution plan", plan)

        ticket = {"incident": incident, "plan": plan, "assignee": "Engineer", "status": "assigned"}
        emit("Incident Responder", "Assignment -> Engineer", self.report(
            "Explain the architect's plan and assignment to the engineer.", ticket))

        fix = engineer.implement(ticket)
        emit("Engineer", "Implementation complete (simulated)", fix)
        ticket["status"] = "awaiting_validation"
        emit("Incident Responder", "Validation request -> Tester", "Validate the simulated fix.")
        validation = tester.validate(ticket, fix)
        emit("Tester", "Validation result (simulated)", validation)

        ticket["status"] = "resolved" if fix["success"] and validation["passed"] else "needs_follow_up"
        result = {"ticket": ticket, "fix": fix, "validation": validation}
        emit("Incident Responder", "Resolution update", self.report(
            "Summarize the final ticket status and the simulated validation evidence.", result))
        emit("Incident Responder", f"{incident['id']} | Final status: {ticket['status'].upper()}")
        return result

