"""Incident reporter -> responder -> architect -> engineer -> tester simulation."""

import argparse
import os
import random

from libs.console import configure_console, emit
from libs.jira_client import FakeJiraAdapter

from agents.architect import Architect, DemoArchitect
from agents.engineer import Engineer
from agents.incident_responder import IncidentResponder
from agents.incident_reporter import IncidentReporter, DemoIncidentReporter, SCENARIOS
from agents.tester import Tester


FAILURES = ("validation", "create", "create-timeout", "engineer", "tester", "unknown")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="Simulate all models without API calls.")
    parser.add_argument("--count", type=int, default=1, help="Number of reports to simulate (default: 1).")
    parser.add_argument("--scenario", help="Optional free-text scenario for the LLM reporter.")
    parser.add_argument("--no-color", action="store_true", help="Disable terminal colors.")
    parser.add_argument("--ticket-adapter", choices=("fake-jira",), help="Optional local-only mock ticket adapter; never contacts Jira.")
    parser.add_argument("--fake-ticket-failure", choices=FAILURES, help="Safe deterministic mock-only fault injection (requires --ticket-adapter fake-jira).")
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count must be at least 1")
    if args.offline and args.scenario:
        parser.error("--scenario requires model mode; offline reports are fixed examples")
    if args.fake_ticket_failure and args.ticket_adapter != "fake-jira":
        parser.error("--fake-ticket-failure requires --ticket-adapter fake-jira")
    configure_console(no_color=args.no_color)

    if args.offline:
        emit("System", "OFFLINE SIMULATION", "All roles simulated; no model calls or production changes.")
        architect = DemoArchitect()
        model = None
        reporter = DemoIncidentReporter()
    else:
        from dotenv import load_dotenv
        from langchain_litellm import ChatLiteLLM
        from langchain_typesafe import TypeSafeClassifier

        load_dotenv()
        architect = Architect(TypeSafeClassifier())
        model = ChatLiteLLM(model="openai/" + os.getenv("LM_STUDIO_MODEL", "google/gemma-4-e4b"), api_base=os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1"), api_key=os.getenv("LM_STUDIO_API_KEY", "lm-studio"), temperature=0)
        reporter = IncidentReporter(ChatLiteLLM(model="openai/" + os.getenv("LM_STUDIO_MODEL", "google/gemma-4-e4b"), api_base=os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1"), api_key=os.getenv("LM_STUDIO_API_KEY", "lm-studio"), temperature=0.8))
        emit("System", "MODEL SIMULATION", "LLM reporter and responder | System One architect | Static engineer and tester")

    adapter = None
    if args.ticket_adapter == "fake-jira":
        create_mode = {"create": "create_error", "create-timeout": "ambiguous_timeout"}.get(args.fake_ticket_failure, "none")
        adapter = FakeJiraAdapter(create_mode=create_mode)
        emit("Fake Jira Adapter", "LOCAL MOCK ENABLED", "In-memory synthetic records only; no credential or network use.")

    emit("Architect", "Ready", {"runbooks loaded": len(architect.catalog)})
    responder = IncidentResponder(model, ticket_adapter=adapter)
    engineer = Engineer(fail=args.fake_ticket_failure == "engineer")
    tester = Tester(fail=args.fake_ticket_failure == "tester")
    results = []
    scenarios = random.sample(SCENARIOS, k=len(SCENARIOS))
    for index in range(args.count):
        incident = reporter.report(index if args.offline else (args.scenario or scenarios[index % len(scenarios)]))
        if args.fake_ticket_failure == "validation":
            incident["evidence"] = ""  # deliberately rejected before create
        elif args.fake_ticket_failure == "unknown":
            incident["evidence"] = "unrecognized synthetic signal with insufficient evidence"
            incident["impact"] = "Synthetic impact is not classified by the bundled runbooks."
        emit("System", f"INCIDENT {index + 1} / {args.count}")
        emit("Incident Reporter", "Report -> Incident Responder", incident)
        results.append(responder.resolve(incident, architect, engineer, tester))
    summary = {}
    for result in results:
        ticket = result["ticket"]
        plan = ticket["plan"]
        summary[ticket["incident"]["id"]] = f"{plan['incident_type']} | {plan['priority']} | {plan['action']} | {ticket['status'].upper()}"
    emit("System", "FINAL SUMMARY", summary)


if __name__ == "__main__":
    main()
