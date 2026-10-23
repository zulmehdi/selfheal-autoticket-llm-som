"""Static engineer for the incident simulation."""


class Engineer:
    def implement(self, ticket):
        return {
            "success": True,
            "message": "Fix successfully implemented in the simulated environment.",
            "completed_steps": ticket["plan"]["steps"],
        }

