"""Incident reporter -> responder -> architect -> engineer -> tester simulation."""

import argparse
import os
import random

from libs.console import configure_console, emit

from agents.architect import Architect, DemoArchitect
from agents.engineer import Engineer
from agents.incident_responder import IncidentResponder
from agents.incident_reporter import IncidentReporter, DemoIncidentReporter, SCENARIOS
from agents.tester import Tester

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="Simulate all models without API calls.")
    parser.add_argument("--count", type=int, default=1, help="Number of reports to simulate (default: 1).")
    parser.add_argument("--scenario", help="Optional free-text scenario for the LLM reporter.")
    parser.add_argument("--no-color", action="store_true", help="Disable terminal colors.")
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count must be at least 1")
    if args.offline and args.scenario:
        parser.error("--scenario requires model mode; offline reports are fixed examples")
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
        model = ChatLiteLLM(
            model="openai/" + os.getenv("LM_STUDIO_MODEL", "google/gemma-4-e4b"),
            api_base=os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1"),
            api_key=os.getenv("LM_STUDIO_API_KEY", "lm-studio"),
            temperature=0,
        )
        reporter = IncidentReporter(ChatLiteLLM(
            model="openai/" + os.getenv("LM_STUDIO_MODEL", "google/gemma-4-e4b"),
            api_base=os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1"),
            api_key=os.getenv("LM_STUDIO_API_KEY", "lm-studio"),
            temperature=0.8,
        ))
        emit("System", "MODEL SIMULATION", "LLM reporter and responder | System One architect | Static engineer and tester")

    emit("Architect", "Ready", {"runbooks loaded": len(architect.catalog)})
    responder = IncidentResponder(model)
    engineer, tester = Engineer(), Tester()
    results = []
    # Single-report runs should not always start with the deployment scenario.
    scenarios = random.sample(SCENARIOS, k=len(SCENARIOS))
    for index in range(args.count):
        incident = reporter.report(index if args.offline else (args.scenario or scenarios[index % len(scenarios)]))
        emit("System", f"INCIDENT {index + 1} / {args.count}")
        emit("Incident Reporter", "Report -> Incident Responder", incident)
        results.append(responder.resolve(incident, architect, engineer, tester))
    summary = {}
    for result in results:
        ticket = result["ticket"]
        plan = ticket["plan"]
        summary[ticket['incident']['id']] = (
            f"{plan['incident_type']} | {plan['priority']} | {plan['action']} | {ticket['status'].upper()}"
        )
    emit("System", "FINAL SUMMARY", summary)


if __name__ == "__main__":
    main()


