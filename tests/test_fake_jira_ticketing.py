"""No-network tests for the typed local mock ticket adapter and orchestration seam."""

import unittest

from agents.architect import DemoArchitect
from agents.engineer import Engineer
from agents.incident_responder import IncidentResponder
from agents.incident_reporter import OFFLINE_REPORTS
from agents.tester import Tester
from libs.jira_client import FakeJiraAdapter, FakeTicketCreateError


def incident(**changes):
    value = {"id": "INC-unit000", **OFFLINE_REPORTS[0]}
    value.update(changes)
    return value


class FakeTicketingTests(unittest.TestCase):
    def resolve(self, adapter, *, engineer_fail=False, tester_fail=False, data=None):
        return IncidentResponder(None, adapter).resolve(
            data or incident(), DemoArchitect(), Engineer(engineer_fail), Tester(tester_fail)
        )

    def test_ticket_retains_classification_and_local_mock_metadata(self):
        adapter = FakeJiraAdapter(assignee_fixture="fixture-user-not-an-account")
        result = self.resolve(adapter)
        fake = result["mock_ticket"]
        self.assertEqual(fake.key, "SIM-1")
        self.assertTrue(fake.url.startswith("https://jira.example.invalid/browse/SIM-1"))
        self.assertEqual(fake.request.incident_id, "INC-unit000")
        self.assertTrue(fake.request.correlation_id.startswith("EXT-"))
        self.assertEqual(fake.request.incident_category, "deployment_regression")
        self.assertEqual(fake.request.priority, "P1")
        self.assertEqual(fake.request.runbook_id, "RB-001")
        self.assertTrue(fake.request.planned_steps)
        self.assertEqual(fake.request.assignee_fixture, "fixture-user-not-an-account")
        self.assertEqual(fake.local_lifecycle, "SIMULATED_VALIDATED_LOCAL_ONLY")
        self.assertEqual(len(fake.comments), 3)
        self.assertTrue(all("[SIMULATION/MOCK]" in item.body for item in fake.comments))
        self.assertIn("role Engineer", fake.comments[0].body)

    def test_report_validation_happens_before_fake_creation(self):
        adapter = FakeJiraAdapter()
        with self.assertRaisesRegex(ValueError, "requires nonempty"):
            self.resolve(adapter, data=incident(evidence=""))
        self.assertEqual(adapter.tickets, ())

    def test_injected_create_failure_has_no_ticket(self):
        adapter = FakeJiraAdapter(create_mode="create_error")
        with self.assertRaises(FakeTicketCreateError):
            self.resolve(adapter)
        self.assertEqual(adapter.tickets, ())

    def test_ambiguous_timeout_reconciles_without_duplicate(self):
        adapter = FakeJiraAdapter(create_mode="ambiguous_timeout")
        result = self.resolve(adapter)
        self.assertEqual(result["mock_ticket"].key, "SIM-1")
        self.assertEqual(len(adapter.tickets), 1)
        self.assertIs(adapter.find_by_correlation(result["mock_ticket"].request.correlation_id), result["mock_ticket"])

    def test_engineer_or_tester_failure_needs_local_follow_up(self):
        for engineer_fail, tester_fail in ((True, False), (False, True)):
            with self.subTest(engineer_fail=engineer_fail, tester_fail=tester_fail):
                result = self.resolve(FakeJiraAdapter(), engineer_fail=engineer_fail, tester_fail=tester_fail)
                self.assertEqual(result["ticket"]["status"], "needs_follow_up")
                self.assertEqual(result["mock_ticket"].local_lifecycle, "SIMULATED_NEEDS_FOLLOW_UP")
                self.assertNotIn("RESOLVED", result["mock_ticket"].local_lifecycle)

    def test_unknown_fallback_is_recorded_on_mock_ticket(self):
        result = self.resolve(FakeJiraAdapter(), data=incident(
            evidence="unrecognized synthetic signal with insufficient evidence",
            impact="Synthetic impact is not classified by the bundled runbooks.",
        ))
        self.assertEqual(result["ticket"]["plan"]["incident_type"], "unknown")
        self.assertEqual(result["mock_ticket"].request.incident_category, "unknown")


if __name__ == "__main__":
    unittest.main()
