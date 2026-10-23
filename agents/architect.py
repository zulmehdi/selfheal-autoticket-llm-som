"""System One architect and its offline stand-in."""

from libs.runbook_loader import RUNBOOK_DIR, load_runbooks


def build_plan(incident_type, catalog):
    """Keep each type's priority and runbook together, including unknown results."""
    if incident_type not in catalog:
        incident_type = "unknown"
    entry = catalog[incident_type]
    return {
        "incident_type": incident_type,
        "priority": entry["priority"],
        "runbook_id": entry["runbook"]["id"],
        "runbook_source": entry["runbook"]["source"],
        "action": entry["runbook"]["action"],
        "steps": list(entry["runbook"]["steps"]),
        "guidance": dict(entry["runbook"]["context"]),
        "validation_checks": list(entry["runbook"]["validation_checks"]),
    }


class Architect:
    """System One chooses typed decisions; the runbook supplies the prose steps."""

    def __init__(self, classifier, runbook_dir=RUNBOOK_DIR):
        self.classifier = classifier
        self.catalog = load_runbooks(runbook_dir)

    def decide(self, incident):
        from langchain_typesafe import Choice

        catalog = self.catalog
        response = self.classifier.invoke({
            "state": {"incident": incident, "incident_catalog": catalog},
            "questions": {
                "incident_type": Choice(
                    instructions="Identify which incident type matches the observed symptoms and evidence. "
                    "Do not infer the type from ticket IDs or exact wording. Choose unknown if no known type fits.",
                    criteria={name: entry["description"] for name, entry in catalog.items()},
                ),
            },
        })
        answer = response.choices["incident_type"]
        plan = build_plan(answer.choice, catalog)
        plan["confidence"] = {"incident_type": answer.confidence}
        return plan


class DemoArchitect:
    """Deterministic stand-in for System One, used only with --offline."""

    def __init__(self, runbook_dir=RUNBOOK_DIR):
        self.catalog = load_runbooks(runbook_dir)

    def decide(self, incident):
        # Simple fixture rules for the bundled reports, not a substitute for System One.
        evidence = incident["evidence"].lower()
        if "connection pool exhausted" in evidence:
            incident_type = "database_connection_exhaustion"
        elif "certificate expired" in evidence:
            incident_type = "expired_tls_certificate"
        elif "queue backlog" in evidence:
            incident_type = "message_queue_backlog"
        elif "just after deployment" in evidence:
            incident_type = "deployment_regression"
        elif "instances fail health" in evidence:
            incident_type = "unhealthy_instances"
        elif "warning" in evidence and "no customer impact" in incident["impact"].lower():
            incident_type = "unexplained_warning"
        else:
            incident_type = "unknown"
        return build_plan(incident_type, self.catalog)

