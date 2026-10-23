"""Static tester for the incident simulation."""


class Tester:
    def __init__(self, fail=False):
        self.fail = fail

    def validate(self, ticket, fix):
        return {
            "passed": not self.fail,
            "message": (
                "Injected simulated validation failure; no production validation was performed."
                if self.fail else f"Validation successful for {ticket['incident']['service']} (simulated)."
            ),
            "checks_passed": [] if self.fail else ticket["plan"]["validation_checks"],
        }
