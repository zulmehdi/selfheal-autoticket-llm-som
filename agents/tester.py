"""Static tester for the incident simulation."""


class Tester:
    def validate(self, ticket, fix):
        return {
            "passed": True,
            "message": f"Validation successful for {ticket['incident']['service']} (simulated).",
            "checks_passed": ticket["plan"]["validation_checks"],
        }

