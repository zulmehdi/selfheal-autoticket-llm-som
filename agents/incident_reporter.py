"""Generate synthetic operational reports without access to classification rules."""

import json
from uuid import uuid4


SCENARIOS = [
    "Inventory reservations started failing for everyone immediately after a software release.",
    "Product search intermittently times out; two search nodes fail health probes without a recent release.",
    "An analytics ingestion job logs unfamiliar warnings, but data still arrives on time.",
    "A customer profile database refuses connections because its connection pool is exhausted.",
    "Employees cannot sign in to the internal portal; the identity gateway presents an expired TLS certificate.",
    "Notification emails arrive late because the message queue grows faster than workers can process it.",
]

OFFLINE_REPORTS = [
    {
        "service": "inventory-api",
        "summary": "Every stock reservation returns an error.",
        "impact": "All warehouses have been unable to reserve stock for eight minutes.",
        "evidence": "HTTP 500 responses started just after deployment. The previous release worked; database checks pass.",
    },
    {
        "service": "product-search",
        "summary": "Product searches sometimes hang instead of returning results.",
        "impact": "About 20% of search requests time out; other site functions work.",
        "evidence": "Two instances fail health probes. No recent deployment. Search index and network checks pass.",
    },
    {
        "service": "analytics-ingestion",
        "summary": "A parser warning repeats in the ingestion job logs.",
        "impact": "No customer impact; dashboards remain fresh and event counts are normal.",
        "evidence": "A warning repeats every minute. No records are dropped. All instances are healthy; its cause is unknown.",
    },
    {
        "service": "customer-profile-db",
        "summary": "Profile pages fail to load while the home page works.",
        "impact": "All profile reads fail; other services are available.",
        "evidence": "Database connection pool exhausted: 200 of 200 sessions used, with many long-running idle transactions. No recent release or storage alarm.",
    },
    {
        "service": "employee-identity-gateway",
        "summary": "Employees see a certificate error when signing in.",
        "impact": "All staff are blocked from the internal portal; existing sessions continue.",
        "evidence": "The identity gateway TLS certificate expired 12 minutes ago. Handshake probes fail; backend health checks pass.",
    },
    {
        "service": "notification-workers",
        "summary": "Order confirmation emails arrive 25 minutes late.",
        "impact": "Notifications are delayed for some customers, but purchases succeed.",
        "evidence": "Message queue backlog is 48000 items and growing. Worker throughput is below the arrival rate; no failed deliveries or provider throttling observed.",
    },
]


class IncidentReporter:
    def __init__(self, model):
        self.model = model

    def report(self, scenario):
        response = self.model.invoke([
            ("system", "You simulate a person or monitoring system reporting an incident. "
             "Invent one realistic synthetic report using the service and failure described in the scenario. "
             "Use varied services such as inventory, search, analytics, databases, identity, or notifications. "
             "Describe observations, timestamps or durations, customer impact, and evidence; "
             "do not prescribe a fix, severity, priority, category, or runbook. "
             "Return only a JSON object with four nonempty string fields: "
             "service, summary, impact, evidence. Do not use Markdown fences."),
            ("human", scenario),
        ])
        content = response.content
        if not isinstance(content, str):
            raise ValueError("Incident reporter must return text containing a JSON object")
        # Tolerate a model wrapping the otherwise valid JSON in a code fence.
        text = content.strip()
        if text.startswith("```") and text.endswith("```"):
            text = "\n".join(text.splitlines()[1:-1])
        try:
            report = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("Incident reporter returned invalid JSON; try generating again") from exc
        fields = ("service", "summary", "impact", "evidence")
        if not isinstance(report, dict) or any(
            not isinstance(report.get(key), str) or not report[key].strip()
            for key in fields
        ):
            raise ValueError("Incident reporter requires nonempty service, summary, impact, and evidence strings")
        # Only observations cross the boundary, even if the model adds labels.
        return {"id": f"INC-{uuid4().hex[:8]}", **{key: report[key].strip() for key in fields}}


class DemoIncidentReporter:
    """Fixed observational reports for reproducible offline testing."""

    def report(self, index):
        return {"id": f"INC-{uuid4().hex[:8]}", **OFFLINE_REPORTS[index % len(OFFLINE_REPORTS)]}
