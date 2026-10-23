"""Static engineer for the incident simulation."""


class Engineer:
    def __init__(self, fail=False):
        self.fail = fail

    def implement(self, ticket):
        return {
            "success": not self.fail,
            "message": (
                "Injected simulated engineer failure; no remediation was performed."
                if self.fail else "Fix successfully implemented in the simulated environment."
            ),
            "completed_steps": [] if self.fail else ticket["plan"]["steps"],
        }
